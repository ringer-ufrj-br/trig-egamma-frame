import os
from typing import Dict, Iterable, Iterator, Any
from glob import iglob


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


def dump_script_report(
        files: Iterable[str],
        filepath: str,
        n_samples: int = None):
    """
    Dumps a report of the files processed by a script to a file

    Parameters
    ----------
    files : Iterable[str]
        Iterable with the files processed
    filepath : str
        Path to the file to dump the report
    n_samples : int, optional
        Number of samples processed, by default None
    """
    if not filepath.endswith('.txt'):
        filepath += '.txt'
    with open(filepath, 'w') as f:
        if n_samples:
            f.write(f'Number of samples: {n_samples}\n')
        f.write('Files:\n')
        n_files = 0
        for file in files:
            f.write(f'{file}\n')
            n_files += 1
        f.write(f'Number of files: {n_files}\n')


def check_list_sizes(args: dict, lists2check: list):
    """
    Checks if the lists in a dictionary have the same length.
    Helps if argument parsing inside scripts.

    Parameters
    ----------
    args : dict
        Dictionary with the lists to check
    lists2check : list
        List with the names of the lists to check

    Raises
    ------
    ValueError
        Raised if the lists do not have the same length
    """
    list_len = len(args[lists2check[0]])
    for list_name in lists2check[1:]:
        if len(args[list_name]) != list_len:
            raise ValueError(
                f'{", ".join(lists2check)} must have the same length'
            )
