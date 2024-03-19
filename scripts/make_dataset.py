import os
import json
import logging
import logging.config
from typing import Any, Dict, Iterator, List, Tuple
from ringer.constants import LOGGING_CONFIG
from argparse import ArgumentParser
from ringer.dataset import dump_dataset_rdf
from ringer.root import get_tchain
from ringer.script_utils import check_list_sizes
from ringer.utils import open_directories
from tqdm import tqdm
import ROOT
import numpy as np
import pandas as pd

LOGGER_NAME = 'ringer_debug'
logging.config.dictConfig(LOGGING_CONFIG)


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
        required=True,
        nargs='+',
        help='The target variable to be used in the'
        ' dataset according to filepaths'
    )
    parser.add_argument(
        '--target-labels',
        required=True,
        nargs='+',
        dest='target_labels',
        help='The target labels to be used in the dataset'
        ' The labels are dumped in a .json file in the dataset dir'
    )
    parser.add_argument(
        '--rings-field-name',
        required=True,
        dest='rings_field_name',
        help='Name of the rings field in the root tree'
        ' to open the vector`into separate columns'
    )
    parser.add_argument(
        '--n-rings',
        type=int,
        required=True,
        dest='n_rings',
        help='Number of the rings in the vector to open'
    )
    parser.add_argument(
        '--add-id',
        required=True,
        action='store_true',
        help='If passed, adds an integer id column to the dataset'
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
        help='Filters to apply to the tree'
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

    check_list_sizes(args, ['filepaths', 'targets'])
    if args['definition_names'] or args['definition_ops']:
        check_list_sizes(args, ['definition_names', 'definition_ops'])

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
         targets: List[str], rings_field_name: str, n_rings: int,
         add_id: bool, filters: list, target_labels: Dict[Any, Any],
         definition_names: list, definition_ops: list,
         mt: bool, dev: bool, id_offset: int = 0):

    if mt:
        ROOT.EnableImplicitMT()

    file_target_df = pd.DataFrame(
        {'filepaths': filepaths, 'targets': targets}
    )
    iterator = tqdm(
        enumerate(file_target_df.groupby('targets')),
        desc='Processing target', unit='target',
        total=file_target_df['targets'].nunique()
    )
    for file_num, (target, target_df) in iterator:

        # logger.info(f'Processing {filepath}')
        _, chain = get_tchain(target_df['filepaths'].to_list(), treepath)
        rdf = ROOT.RDataFrame(chain) \
            .Define('target', str(target))

        if definition_names:
            for name, op in zip(definition_names, definition_ops):
                rdf = rdf.Define(name, op)

        if filters:
            filter_str = ' && '.join(filters)
            rdf = rdf.Filter(filter_str)

        if add_id:
            rdf = rdf.Define('id', f'rdfentry_ + {id_offset}')
            id_offset += rdf.Count().GetValue()

        col_names = np.array(rdf.GetColumnNames(), dtype=object)
        col_names = col_names[col_names != rings_field_name]
        col_names = col_names.tolist()

        new_ringer_field_name = rings_field_name.replace('rings', 'ring')
        for i in range(n_rings):
            new_field_name = f'{new_ringer_field_name}_{i}'
            col_names.append(new_field_name)
            rdf = rdf.Define(
                new_field_name,
                f'{rings_field_name}[{i}]'
            )

        dump_dataset_rdf(
            output_dir,
            rdf,
            'data',
            f'{file_num:06d}.root',
            col_names
        )
        del rdf

        if dev and file_num >= 100:
            break

    with open(os.path.join(output_dir, 'target_labels.json'), 'w') as f:
        json.dump(target_labels, f, indent=4)


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    args = parse_args()
    main(**args)
