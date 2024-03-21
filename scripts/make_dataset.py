import os
import json
import logging
import logging.config
from typing import Iterator, List, Tuple
from argparse import ArgumentParser
from egamma.dataset import dump_dataset_rdf
from egamma.utils import dump_script_report, open_directories
from egamma.logging import set_loggers
from tqdm import tqdm
import ROOT
import numpy as np

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
        '--definition-names', required=False, nargs='+',
        dest='definition_names', default=[],
        help='Column names to define in the output files'
    )
    parser.add_argument(
        '--definition-ops', required=False, nargs='+',
        dest='definition_ops', default=[],
        help='Column defintiion operations to apply'
        ' according to definition-names'
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
        '--mt', action='store_true',
        help='If passed uses ROOT multithreading'
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
         definition_names: List[str], definition_ops: List[str],
         no_export_definitions: bool, new_filename: bool,
         mt: bool, dev: bool, table_name: str, id_offset: int = 0):

    if mt:
        ROOT.EnableImplicitMT()

    files = np.sort(list(open_directories(filepaths, 'root')))
    iterator = tqdm(
        enumerate(files),
        desc='Processing files', unit='files',
        total=1 if dev else len(files)
    )
    for file_num, filepath in iterator:
        if dev and file_num > 0:
            break

        rdf = ROOT.RDataFrame(treepath, filepath)
        # the rdf method returns a cppyy object with uncompatible
        # python types, so we convert it to a list of strings
        col_names = [str(name) for name in rdf.GetColumnNames()]

        if definition_names:
            for name, op in zip(definition_names, definition_ops):
                rdf = rdf.Define(name, op)
            if not no_export_definitions:
                col_names += definition_names

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

        dump_dataset_rdf(
            output_dir,
            rdf,
            table_name,
            export_filename,
            col_names
        )
        del rdf
    filepath = os.path.join(output_dir, 'dataset_gen_report.txt')
    dump_script_report(files, filepath, id_offset)


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    main(**args)
