from typing import Iterable, Tuple
import ROOT
from egamma.utils.misc import open_directories
import numpy as np


def get_tchain(
        filepaths: Iterable[str],
        treepath: str,
        dev: bool = False,
        sorted: bool = False,
        title: str = 'tchain') -> Tuple[Iterable[str], ROOT.TChain]:
    """
    Receives an iterable of files and directories and returns a TChain with all
    the trees from the .root files contained in that Iterable

    Parameters
    ----------
    filepaths : Iterable[str]
        Iterable containing paths to root files.
        Directories are opnened recursively for root files
    treepath : str
        Path for the tree inside the .root file
    dev : bool
        If true, loads only one file, for testing purposes only
    sorted : bool
        If true, the files are sorted before being added to the TChain
    title: str
        TChain title

    Returns
    -------
    Iterable[str]
        Iterable with all the files processed
    ROOT.TChain
        The TChain contianing all the root files TTrees
    """
    if isinstance(filepaths, str):
        raise TypeError(
            "filepaths should be an iterable of strings, not a string"
        )
    chain = ROOT.TChain(treepath, title)
    files = open_directories(filepaths, 'root')
    if sorted:
        files = np.sort(list(files))
    for filepath in files:
        chain.Add(filepath)
        if dev:
            single_file = filepath
            break
    if dev:
        return [single_file], chain
    else:
        if sorted:
            return files, chain
        else:
            return open_directories(filepaths, 'root'), chain
