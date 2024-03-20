import os
import json
import logging
import logging.config
from typing import List
from argparse import ArgumentParser
from egamma.root import get_tchain
from egamma.utils import open_directories
from egamma.logging import set_loggers
from tqdm import tqdm
import ROOT
import numpy as np

LOGGER_NAME = 'trigger-egamma-frame-debug'


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Adds an id column to the trees of a collection"
        " of root files"
    )
    parser.add_argument(
        '--filepaths',
        required=True,
        nargs='+',
        help='Path to the files to process.'
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
        help='Directory to save the exported dataset.'
        'The files are saved with the format new_{{filename}}'
    )
    parser.add_argument(
        '--id-col-name',
        default='id',
        help='Name of the id column to be added to the dataset'
    )

    args = parser.parse_args().__dict__
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)
    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    args_filepath = os.path.join(args['output_dir'], 'add_id_args.json')
    with open(args_filepath, 'w') as f:
        json.dump(args, f, indent=4)

    return args


def main(filepaths: List[str], treepath: str, output_dir: str,
         id_col_name: str):

    ROOT.EnableImplicitMT()
    files = np.sort(list(open_directories(filepaths, 'root')))

    iterator = tqdm(
        files,
        desc='Processing files:', unit='file',
        total=len(files)
    )
    id_offset = 0
    for filepath in iterator:

        _, chain = get_tchain([filepath], treepath)
        rdf = ROOT.RDataFrame(chain).Define(
            id_col_name,
            f'rdfentry_ + {id_offset}')
        id_offset += rdf.Count().GetValue()
        filename = os.path.basename(filepath)
        output_path = os.path.join(output_dir, f'new_{filename}')
        rdf_columns = rdf.GetColumnNames()
        options = ROOT.RDF.RSnapshotOptions()
        options.fCompressionLevel = 9
        rdf.Snapshot(
            treepath,
            output_path,
            rdf_columns,
            options
        )
        del rdf


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    main(**args)
