import os
import json
import logging
import logging.config
from typing import List
from argparse import ArgumentParser
from egamma.logging import set_loggers
import ROOT
from tqdm import tqdm

LOGGER_NAME = 'trig-egamma-frame-debug'


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Builds a Fake set of ntuples with random distribution"
    )
    parser.add_argument(
        '--output-dir',
        default='./',
        dest='output_dir',
        help='Directory to save the exported dataset'
    )
    parser.add_argument(
        '--column-list',
        required=True,
        nargs='+',
        dest='column_list',
        help='The list of columns to be created in the dataset'
    )
    parser.add_argument(
        '--n-entries',
        required=True,
        type=int,
        dest='n_entries',
        help='The number of entries per file'
    )
    parser.add_argument(
        '--n-files',
        default=1,
        type=int,
        dest='n_files',
        help='The number of files to be created'
    )
    parser.add_argument(
        '--with-id',
        action='store_true',
        dest='with_id',
        help='If passed, the id column is added to the dataset'
    )

    args = parser.parse_args().__dict__
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    args_filepath = os.path.join(args['output_dir'], 'ntuple_gen_args.json')
    with open(args_filepath, 'w') as f:
        json.dump(args, f, indent=4)

    return args


def main(
        output_dir: str,
        column_list: List[str],
        n_entries: int,
        n_files: int,
        with_id: bool) -> None:

    ROOT.EnableImplicitMT()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    iterator = tqdm(
        range(n_files),
        desc='Creating fake ntuples',
        unit='file'
    )
    for i in iterator:
        output_path = os.path.join(output_dir, f'{i:06d}.root')
        rdf = ROOT.RDataFrame(n_entries)
        if with_id:
            rdf = rdf.Define('id', f'rdfentry_ + {i*n_entries}')
        for col in column_list:
            rdf = rdf.Define(col, "gRandom->Rndm()")
        rdf_columns = rdf.GetColumnNames()
        options = ROOT.RDF.RSnapshotOptions()
        options.fCompressionLevel = 9
        rdf.Snapshot(
            'tree',
            output_path,
            rdf_columns,
            options
        )


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Creating fake ntuple')
    main(**args)
    logger.info('Finished creating fake ntuple')
