import os
import numpy as np
import logging
import logging.config
from typing import List
from argparse import ArgumentParser
from egamma.utils.logging import set_loggers
import ROOT
from egamma.utils.root import get_tchain

LOGGER_NAME = 'trig-egamma-frame-debug'


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Tests if the id col in a collection of root "
        "files is unique"
    )
    parser.add_argument(
        '--filepaths',
        dest='filepaths',
        nargs='+',
        help='Path to the files to be tested.',
        required=True
    )
    parser.add_argument(
        '--treepath',
        required=True,
        help='The path to the tree object inside the root file'
    )
    parser.add_argument(
        '--id-col-name',
        default='id',
        dest='id_col_name',
        help='Name of the id column' 
    )

    args = parser.parse_args().__dict__
    return args


def main(
        filepaths: List[str],
        treepath: str,
        id_col_name: str) -> None:

    ROOT.EnableImplicitMT()

    _, chain = get_tchain(filepaths, treepath)
    rdf = ROOT.RDataFrame(chain)
    id_col = rdf.AsNumpy([id_col_name])[id_col_name]
    n_entries = rdf.Count().GetValue()
    n_unique_ids = len(np.unique(id_col))
    logger.info(f'Number of entries: {n_entries}')
    logger.info(f'Number of unique ids: {n_unique_ids}')


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)
    logger.info('Computing unique ids in root files')
    main(**args)
    logger.info('Finished')
