"""
This script is used to build a Machine Learning dataset from root files.
It uses the ROOT RDataFrame to process the files and dump the dataset.
The script receives the filepaths to the root files, the path to the tree
object inside the root files, the output directory, the target variable
to be used in the dataset, the filters to apply to the tree, the columns
to define in the output files, the operations to apply to the defined columns,
and the table name to be used in the dataset.

Known Issues:
Due to problems with C++ bindings in the ROOT RDataFrame, the rdf object
is not properly deleted after the dump_dataset_rdf function is called.
This causes a memory leak that can be seen in the memory usage of the
machine running the script. This issue is not critical for the script
execution, but it can be a problem for long running scripts.

Raises
------
ValueError
    If the target_labels list does not have an even number of elements
RuntimeError
    If there are duplicate filenames in the input files
FileExistsError
    If one of the output files already exists
"""
import os
import json
import logging
import logging.config
from typing import Iterator, List, Tuple, Dict
from argparse import ArgumentParser
from egamma.utils.dataset import dump_dataset_rdf
from egamma.utils.misc import (
    check_list_sizes,
    dump_script_report,
    open_directories
)
from egamma.utils.logging import set_loggers
from tqdm import tqdm
import ROOT
import numpy as np
import pandas as pd

LOGGER_NAME = 'trigger-egamma-frame-debug'


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Builds a Machine Learning dataset from root files"
    )
    parser.add_argument(
        '--filepaths',
        required=True,
        nargs='+',
        help='Path to the files to be converted.'
        'If path is a dir, looks for .root files'
    )
    parser.add_argument(
        '--treepath',
        required=True,
        help='The path to the tree object inside the root file'
    )
    parser.add_argument(
        '--output-dir',
        default='./',
        dest='output_dir',
        help='Directory to save the exported dataset'
    )
    parser.add_argument(
        '--targets',
        required=False,
        nargs='+',
        default=[],
        help='The target variable to be used in the'
        ' dataset according to filepaths'
    )
    parser.add_argument(
        '--target-labels',
        required=False,
        nargs='+',
        dest='target_labels',
        help='The target labels to be used in the dataset'
        ' The labels are dumped in a .json file in the dataset dir'
    )
    parser.add_argument(
        '--open-vectors',
        required=False,
        dest='open_vectors',
        nargs='+',
        help='Field names of vector types in the file'
        ' to open into separate columns with format: field_name_{{n}}'
    )
    parser.add_argument(
        '--size-vectors',
        required=False,
        dest='size_vectors',
        nargs='+',
        type=int,
        help='Size of the vectors to open into separate columns'
    )
    parser.add_argument(
        '--add-id',
        required=True,
        action='store_true',
        help='If passed, adds an integer id column to the dataset. '
        'The id is incremented for each file processed in alphabetical order'
    )
    parser.add_argument(
        '--id-col-name',
        default='id',
        dest='id_col_name',
        help='Name of the id column to be added to the dataset'
    )
    parser.add_argument(
        '--id-offset',
        required=False,
        type=int,
        dest='id_offset',
        default=0,
        help='Offset to start the id column'
    )
    parser.add_argument(
        '--filters', required=False, dest='filters',
        nargs='+',
        help='Filters to apply to the exported tree'
    )
    parser.add_argument(
        '--definitions',
        required=False,
        nargs='+',
        default={},
        help='Defines columns on the dataframe. '
        'Should be on the form <definition_name> <definition_expr> ...'
    )
    parser.add_argument(
        '--no-export-definitions',
        action='store_true',
        help='If passed, the defined columns will not be exported'
    )
    parser.add_argument(
        '--new-filename',
        action='store_true',
        help='If passed, the output files will be named with a number '
        'according to the order of the input files'
    )
    parser.add_argument(
        '--table-name',
        required=True,
        dest='table_name',
        help='Name of the dataset table to be exported'
    )
    parser.add_argument(
        '--dev', action='store_true',
        help='If true parses only the first file found for testing'
    )

    args = parser.parse_args().__dict__
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])
    if args['targets']:
        check_list_sizes(args, ['targets', 'filepaths'])
        if args['target_labels']:
            if len(args['target_labels']) % 2 > 0:
                raise ValueError(
                    'The target_labels must have an even number of elements'
                    ' to be converted to a dictionary'
                )
            args['target_labels'] = dict(zip(
                args['target_labels'][::2], args['target_labels'][1::2]
            ))
        else:
            targets = np.unique(args['targets'])
            args['target_labels'] = dict(zip(targets, targets))
    else:
        args['targets'] = [None for _ in args['filepaths']]
        args['target_labels'] = dict()

    if len(args['definitions']) % 2 != 0:
        raise ValueError(
            'The definitions flag must have an even number of elements'
            ' to be converted to a dictionary'
        )
    args['definitions'] = dict(zip(
        args['definitions'][::2], args['definitions'][1::2]
    ))

    args_filepath = os.path.join(args['output_dir'], 'dataset_gen_args.json')
    with open(args_filepath, 'w') as f:
        json.dump(args, f, indent=4)

    return args


def open_filepaths_with_targets(
        filepaths: List[str],
        targets: List[str]) -> Iterator[Tuple[str, int]]:
    for filepath, target in zip(filepaths, targets):
        open_filepaths = open_directories([filepath], 'root')
        for open_filepath in open_filepaths:
            yield open_filepath, target


def main(filepaths: List[str], treepath: str, output_dir: str,
         open_vectors: List[str], size_vectors: List[int],
         add_id: bool, id_col_name: str, filters: List[str],
         definitions: Dict[str, str],
         no_export_definitions: bool, new_filename: bool,
         dev: bool, table_name: str, id_offset: int,
         targets: List[str], target_labels: Dict[str, str]):

    # Check for file duplicates
    files_target = {'filepaths': [], 'targets': []}
    for filepath, target in open_filepaths_with_targets(filepaths, targets):
        files_target['filepaths'].append(filepath)
        files_target['targets'].append(target)

    files_target = pd.DataFrame(files_target) \
        .sort_values('filepaths', ignore_index=True)

    if not new_filename:
        n_unique = files_target['filepaths'].nunique()
        n = len(files_target['filepaths'])
        if (n_unique != n):
            raise RuntimeError(
                "There are duplicate filenames. "
                "Cannot build dataset without renaming the files"
            )

    iterator = tqdm(
        files_target.iterrows(),
        desc='Processing files', unit='files',
        total=1 if dev else len(files_target)
    )
    for file_num, row in iterator:
        if dev and file_num > 0:
            break

        filepath = row['filepaths']
        target = row['targets']

        rdf = ROOT.RDataFrame(treepath, filepath)
        if target:
            rdf = rdf.Define('target', str(target))
        # the rdf method returns a cppyy object with uncompatible
        # python types, so we convert it to a list of strings
        col_names = [str(name) for name in rdf.GetColumnNames()]

        if definitions:
            for name, op in definitions.items():
                rdf = rdf.Define(name, op)
            if not no_export_definitions:
                col_names += list(definitions.keys())

        if filters:
            filter_str = ' && '.join(filters)
            rdf = rdf.Filter(filter_str)

        if add_id:
            rdf = rdf.Define(id_col_name, f'rdfentry_ + {id_offset}')
            id_offset += rdf.Count().GetValue()
            col_names.append(id_col_name)

        if open_vectors and size_vectors:
            for field_name, size in zip(open_vectors, size_vectors):
                for i in range(size):
                    new_field_name = f'{field_name}_{i}'
                    rdf = rdf.Define(
                        new_field_name,
                        f'{field_name}[{i}]'
                    )
                    col_names.append(new_field_name)
            col_names = list(filter(
                lambda x: x not in open_vectors, col_names
            ))

        if new_filename:
            export_filename = f'{file_num:06d}.root'
        else:
            export_filename = os.path.basename(filepath)
        if os.path.exists(export_filename):
            raise FileExistsError(
                f'The file {export_filename} already exists.'
                ' Cannot overwrite files'
            )
        dump_dataset_rdf(
            output_dir,
            rdf,
            table_name,
            export_filename,
            col_names
        )
        del rdf
    filepath = os.path.join(output_dir, 'dataset_gen_report.txt')
    dump_script_report(
        files_target['filepaths'],
        filepath,
        id_offset
    )
    if target_labels:
        with open(os.path.join(output_dir, 'target_labels.json'), 'w') as f:
            json.dump(target_labels, f, indent=4)


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    main(**args)
