"""
Converts a TTree in a group of root files to a desired file format.
Supported formats can be seen with the --help flag.
"""

import os
from typing import Iterable, List, Union, Dict
from argparse import ArgumentParser
from joblib import Parallel, delayed
from egamma.utils.misc import open_directories
from egamma.utils.schema import Schema
from egamma.utils.logging import set_loggers
from egamma.utils.root import get_tchain
from tqdm import tqdm
import ROOT
import logging

set_loggers()
LOGGER_NAME = 'trig-egamma-frame-debug'

# For some reason, if you call preprocess_dataset inside other functions,
# it will raise an error because the C++ object loses its reference.


def preprocess_dataset(
        filepaths: Iterable[str],
        treepath: str,
        filters: List[str],
        definitions: Dict[str, str]):

    _, tchain = get_tchain(filepaths, treepath, sorted=True)
    rdf = ROOT.RDataFrame(tchain)
    if definitions:
        for name, op in definitions.items():
            rdf = rdf.Define(name, op)

    if filters:
        rdf = rdf.Filter(' && '.join(filters))
    return rdf


def to_tfrecord(
        filepaths: Iterable[str],
        treepath: str,
        output_path: str,
        column_list: List[str],
        filters: List[str],
        definitions: Dict[str, str]):

    from egamma.utils.converters import npy_dict_to_tfrecord

    _, tchain = get_tchain(filepaths, treepath, sorted=True)
    rdf = ROOT.RDataFrame(tchain)
    if definitions:
        for name, op in definitions.items():
            rdf = rdf.Define(name, op)

    if filters:
        rdf = rdf.Filter(' && '.join(filters))

    if column_list:
        numpy_dict = rdf.AsNumpy(column_list)
    else:
        numpy_dict = rdf.AsNumpy()
    npy_dict_to_tfrecord(
        numpy_dict,
        output_path
    )


def to_parquet(
        filepaths: Iterable[str],
        treepath: str,
        output_path: str,
        column_list: List[str],
        filters: List[str],
        definitions: Dict[str, str]):

    import pandas as pd

    _, tchain = get_tchain(filepaths, treepath, sorted=True)
    rdf = ROOT.RDataFrame(tchain)
    if definitions:
        for name, op in definitions.items():
            rdf = rdf.Define(name, op)

    if filters:
        rdf = rdf.Filter(' && '.join(filters))

    if column_list:
        numpy_dict = rdf.AsNumpy(column_list)
    else:
        numpy_dict = rdf.AsNumpy()
    pdf = pd.DataFrame.from_dict(numpy_dict)
    pdf.to_parquet(output_path)


def to_h5(
        filepaths: Iterable[str],
        treepath: str,
        output_path: str,
        column_list: List[str],
        filters: List[str],
        definitions: Dict[str, str]):

    import pandas as pd

    _, tchain = get_tchain(filepaths, treepath, sorted=True)
    rdf = ROOT.RDataFrame(tchain)
    if definitions:
        for name, op in definitions.items():
            rdf = rdf.Define(name, op)

    if filters:
        rdf = rdf.Filter(' && '.join(filters))
    if column_list:
        numpy_dict = rdf.AsNumpy(column_list)
    else:
        numpy_dict = rdf.AsNumpy()
    pdf = pd.DataFrame.from_dict(numpy_dict)
    pdf.to_hdf(output_path, key='df')


function_dict = {
    'tfrecord': to_tfrecord,
    'parquet': to_parquet,
    'h5': to_h5
}


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description="Converts a TTree in a group of root files "
        "to a desired file format."
    )
    parser.add_argument(
        '--filepaths',
        required=True,
        nargs='+',
        help='Path to the files to be converted.'
        'If path is a dir, the script looks for .root files'
    )
    parser.add_argument(
        '--treepath',
        required=True,
        help='The path to the tree object inside the root file'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        dest='output_dir',
        help='Directory to save the resulting file'
    )
    parser.add_argument(
        '--output-ext',
        default='parquet',
        dest='output_ext',
        choices=list(function_dict.keys()),
        help='Extension of the output file'
    )
    parser.add_argument(
        '--output-name',
        default=None,
        dest='output_name',
        help='The name of the output file'
        'If merge is not passed adds the file number to the end.'
    )
    parser.add_argument(
        '--column-list',
        nargs='+',
        default=[],
        dest='column_list',
        help='List of columns to be converted.'
    )
    parser.add_argument(
        '--n-jobs',
        default=-1,
        type=int,
        dest='n_jobs',
        help='Number of parallel jobs to instantiate. '
        'If n-jobs <=0, the total number of cpus is used. '
        'Only used if the merge flag is not passed.'
    )
    parser.add_argument(
        '--merge',
        action='store_true',
        help='If passed, the output files are merged into a single file. '
        'When merge is passed, the n-jobs flag is ignored. '
        'Meging the data requires to load all the data into memory. '
        'This could be problematic for low memory machines.'
    )
    parser.add_argument(
        '--filters', required=False, dest='filters',
        nargs='+',
        help='Filters to apply before converting the file.'
        ' Useful when needing to convert just a subset of the data'
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
        '--dev', action='store_true',
        help='If true parses only the first file found for testing'
    )

    args = parser.parse_args().__dict__
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)

    if len(args['definitions']) % 2 != 0:
        raise ValueError(
            'The definitions flag must have an even number of elements'
            ' to be converted to a dictionary'
        )
    args['definitions'] = dict(zip(
        args['definitions'][::2], args['definitions'][1::2]
    ))

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    return args


def get_output_path(
        output_name: Union[str, None],
        output_dir: str,
        output_ext: str
        ):
    if not output_name.endswith(output_ext):
        output_name = f'{output_name}.{output_ext}'
    return os.path.join(output_dir, output_name)


def distributed_convert(
        filepaths: Iterable[str],
        treepath: str,
        output_dir: str,
        output_ext: str,
        output_name: str,
        column_list: List[str],
        filters: List[str],
        definitions: Dict[str, str],
        dev: bool
        ):

    if args['n_jobs'] <= 0:
        pool = Parallel(backend='multiprocessing')
    else:
        pool = Parallel(args['n_jobs'], backend='multiprocessing')
    func = function_dict[output_ext]
    all_directories = open_directories(
        filepaths,
        'root'
    )
    if dev:
        all_directories = [next(all_directories)]
    pool(delayed(func)(
        [filepath],
        treepath,
        get_output_path(
            (os.path.basename(filepath) if
                output_name is None else
                f'{output_name}_{i:06d}.{output_ext}'),
            output_dir,
            output_ext
        ),
        column_list,
        filters,
        definitions)
        for i, filepath in tqdm(enumerate(all_directories))
    )


if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    sample_filepath = next(open_directories(
        args['filepaths'],
        'root',
        True))
    rdf = ROOT.RDataFrame(args['treepath'], sample_filepath)
    if args['column_list'] == 'all' or len(args['column_list']) == 0:
        args['column_list'] = rdf.GetColumnNames()
    if args['definitions']:
        for name, op in args['definitions'].items():
            rdf = rdf.Define(name, op)
    if args['filters']:
        rdf = rdf.Filter(' && '.join(args['filters']))
    schema = Schema.from_numpy_dict(rdf.AsNumpy(args['column_list']))
    schema.to_json(
        os.path.join(args['output_dir'], 'schema.json'),
        exist_ok=True
    )
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Starting conversion')
    if args['merge']:
        if args['dev']:
            filepaths = [next(open_directories(args['filepaths'], 'root'))]
        else:
            filepaths = args['filepaths']
        convert_func = function_dict[args['output_ext']]
        out_path = get_output_path(
                (os.path.basename(args['output_name']) if
                    args['output_name'] is None else args['output_name']),
                args['output_dir'],
                args['output_ext'])
        logger.info(f"Dumping at {out_path}")
        convert_func(
            filepaths,
            args['treepath'],
            get_output_path(
                (os.path.basename(args['output_name']) if
                    args['output_name'] is None else args['output_name']),
                args['output_dir'],
                args['output_ext']),
            args['column_list'],
            args['filters'],
            args['definition_names'],
            args['definition_exprs']
        )
    else:
        distributed_convert(
            args['filepaths'],
            args['treepath'],
            args['output_dir'],
            args['output_ext'],
            args['column_list'],
            args['filters'],
            args['definition_names'],
            args['definition_exprs']
        )
    logger.info('Finished all files')
