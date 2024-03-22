import os
from typing import Iterable, List
from argparse import ArgumentParser
from joblib import Parallel, delayed
from egamma.utils import check_list_sizes, open_directories
from egamma.schema import Schema
from egamma.logging import set_loggers
from egamma.root import get_tchain
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
        definition_names: List[str],
        definition_ops: List[str]):

    _, tchain = get_tchain(filepaths, treepath)
    rdf = ROOT.RDataFrame(tchain)
    if definition_names and definition_ops:
        for name, op in zip(definition_names, definition_ops):
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
        definition_names: List[str],
        definition_ops: List[str]):

    from egamma.converters import npy_dict_to_tfrecord

    _, tchain = get_tchain(filepaths, treepath)
    rdf = ROOT.RDataFrame(tchain)
    if definition_names and definition_ops:
        for name, op in zip(definition_names, definition_ops):
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
        definition_names: List[str],
        definition_ops: List[str]):

    import pandas as pd

    _, tchain = get_tchain(filepaths, treepath)
    rdf = ROOT.RDataFrame(tchain)
    if definition_names and definition_ops:
        for name, op in zip(definition_names, definition_ops):
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
        definition_names: List[str],
        definition_ops: List[str]):

    import pandas as pd

    _, tchain = get_tchain(filepaths, treepath)
    rdf = ROOT.RDataFrame(tchain)
    if definition_names and definition_ops:
        for name, op in zip(definition_names, definition_ops):
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
        default='./',
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

    args = parser.parse_args().__dict__
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)

    check_list_sizes(args, ['definition_names', 'definition_ops'])

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    return args


def get_output_path(filepath: str, output_dir: str, output_ext: str):
    filename = os.path.basename(filepath)
    filename = '.'.join(filename.split('.')[:-1])
    return os.path.join(output_dir, f'{filename}.{output_ext}')


def distributed_convert(
        filepaths: Iterable[str],
        treepath: str,
        output_dir: str,
        output_ext: str,
        column_list: List[str],
        filters: List[str],
        definition_names: List[str],
        definition_ops: List[str]
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
    pool(delayed(func)(
        [filepath],
        treepath,
        get_output_path(filepath, output_dir, output_ext),
        column_list,
        filters,
        definition_names,
        definition_ops)
        for filepath in tqdm(all_directories)
    )


if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    sample_filepath = list(open_directories(
        args['filepaths'],
        'root',
        True))[0]
    rdf = ROOT.RDataFrame(args['treepath'], sample_filepath)
    if args['column_list'] == 'all':
        args['column_list'] = rdf.GetColumnNames()
    schema = Schema.from_numpy_dict(rdf.AsNumpy())
    schema.to_json(
        os.path.join(args['output_dir'], 'schema.json'),
        exist_ok=True
    )
    logger = logging.getLogger(LOGGER_NAME)
    logger.info('Starting conversion')
    if args['merge']:
        convert_func = function_dict[args['output_ext']]
        convert_func(
            args['filepaths'],
            args['treepath'],
            get_output_path(
                'converted.root',
                args['output_dir'],
                args['output_ext']),
            args['column_list'],
            args['filters'],
            args['definition_names'],
            args['definition_ops']
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
            args['definition_ops']
        )
    logger.info('Finished all files')
