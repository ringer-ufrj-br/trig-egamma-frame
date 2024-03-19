from typing import Iterable, Tuple
import ROOT
from egamma.utils import open_directories


def get_tchain(
        filepaths: Iterable[str],
        treepath: str,
        dev: bool = False
        ) -> Tuple[Iterable[str], ROOT.TChain]:
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

    Returns
    -------
    Iterable[str]
        Iterable with all the files processed
    ROOT.TChain
        The TChain contianing all the root files TTrees
    """
    chain = ROOT.TChain(treepath)
    for filepath in open_directories(filepaths, 'root'):
        chain.Add(filepath)
        if dev:
            single_file = filepath
            break
    if dev:
        return [single_file], chain
    else:
        return open_directories(filepaths, 'root'), chain
