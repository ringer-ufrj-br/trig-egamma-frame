import logging
import os
from datetime import datetime
from typing import Dict, Iterable, Iterator, Tuple, Any
from numbers import Number
import numpy as np
from glob import iglob


def get_logger(name: str, id=False, stream=True, file=True):
    logger = logging.getLogger(name)
    if logger.hasHandlers():  # Logger already exists
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    if file:
        now = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        id = os.get_pid() if id else ''
        log_filename = f'{now}_{id}_{name}.log'
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


def get_number_order(num: Number) -> np.integer:
    """
    Returns the order of a number in base 10
    Example:
    >>> get_number_order(100)
    2
    >>> get_number_order(0.1)
    -1

    Parameters
    ----------
    num : Number
        Number to extract the order

    Returns
    -------
    np.integer
        The number order in base 10
    """
    # Comment on the side is to avoid type checking errors
    # with python linting tools
    return np.floor(np.log10(np.abs(num)))  # type: ignore


def significant_around(val: Number,
                       err: Number) -> Tuple[np.floating, np.floating]:
    """
    Rounds a value and its error to the same order of magnitude,
    defined by the error value

    Parameters
    ----------
    val : Number
        Measured value
    err : Number
        Error over the measured value

    Returns
    -------
    Tuple[np.floating, np.floating]
        The rounded value and error
    """
    err_order = get_number_order(err)
    val_arounded = np.around(val, -err_order)  # type: ignore
    err_arounded = np.around(err, -err_order)  # type: ignore
    return val_arounded, err_arounded


def confidence_interval_str(val: Number, err: Number,
                            latex: bool = False, max_precision=5) -> str:
    """
    Returns a string representation of a value and its error
    in latex synthax

    Parameters
    ----------
    val : Number
        Value to be represented
    err : Number
        value error
    latex : bool, optional
        If true adds latex $$ for math mode, by default False
    max_precision : int, optional
        If the measurement precision exceeds max_precision
        only max_precision decimals are printed, by default 5

    Returns
    -------
    str
        String representation of the value and its error
    """
    rtol = 10**(-max_precision)
    if np.isclose(err, 0, rtol=rtol):
        repr_str = f'{val:.{max_precision}f}'
        return repr_str

    calc_precision = int(-get_number_order(err))  # type: ignore
    if calc_precision < max_precision:
        precision = calc_precision
    else:
        precision = calc_precision
    pm = '\\pm' if latex else '+-'
    repr_str = f'{val:.{precision}f} {pm} {err:.{precision}f}'
    if latex:
        repr_str = f'${repr_str}$'
    return repr_str


def get_instance_from_dict(config_dict: Dict[str, str]) -> Any:
    """
    Returns an instance of a class from a dictionary with the
    class name, its arguments and keyword arguments

    Parameters
    ----------
    config_dict : Dict[str, str]
        Dictionary with the class name, its arguments and keyword arguments
        Example:
        {
            'class_name': 'module.submodule.ClassName',
            'args': [1, 2, 3],
            'kwargs': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        Created instance:
        module.submodule.ClassName(1, 2, 3, key1='value1', key2='value2')

    Returns
    -------
    Any
        Instance of the class defined in the config_dict
    """

    splitted_name = config_dict['class_name'].split('.')
    module_name = splitted_name[0]
    attr_name_list = splitted_name[1:]
    module = __import__(module_name)
    attr = module
    for attr_name in attr_name_list:
        attr = getattr(attr, attr_name)

    attr_instance = attr(
        *config_dict['args'],
        **config_dict['kwargs']
    )

    return attr_instance


def is_instance(obj: Any, class_: Any, var_name: str) -> None:
    """
    Raises a TypeError if the object is not an instance of a class

    Parameters
    ----------
    obj : Any
        Object to check
    class_ : Any
        Class to check if the object is an instance of
    var_name : str
        Name of the variable to be checked

    Raises
    ------
    TypeError
        Raised if the object is not an instance of the class
    """
    if not isinstance(obj, class_):
        raise TypeError(f'{var_name} must be of type {class_.__name__}')


def remove_file_ext(filename: str) -> str:
    """
    Removes the file extension from a filename

    Parameters
    ----------
    filename : str
        Filename to remove the extension

    Returns
    -------
    str
        Filename without the extension
    """
    return '.'.join(filename.split('.')[:-1])


def open_directories(
        paths: Iterable[str],
        file_ext: str,
        dev: bool = False) -> Iterator[str]:
    """
    Generator that opens all directories in an iterator for
    a specific file extension. This is useful for script cases where
    an user can pass a mix of directories and filepaths.

    Parameters
    ----------
    paths : Iterable[str]
        Iterable with file or dir paths to look for files with file_ext
    file_ext : str
        Te desired file extension to look for
    dev: bool
        If True, the function will yield just the first file found

    Yields
    ------
    str
        The path to a file

    Raises
    ------
    ValueError
        Raised if there is a file that doesn not have file_ext as its extension
    """
    for i, ipath in enumerate(paths):
        if os.path.isdir(ipath):
            dir_paths = iglob(
                os.path.join(ipath, '**', f'*.{file_ext}'),
                recursive=True
            )
            for open_path in open_directories(dir_paths, file_ext):
                yield open_path
        elif ipath.endswith(f'.{file_ext}'):
            yield ipath
        else:
            raise ValueError(
                f'{ipath} does not have the expected {file_ext} extension'
            )
        if dev and i > 0:
            break
