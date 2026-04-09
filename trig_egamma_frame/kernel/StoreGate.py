

__all__ = ['StoreGate','restoreStoreGate']

from ROOT import TFile
import numpy as np
import traceback
import os.path
import gc
import collections
from typing import Any, Dict, List, Optional, Iterator, Tuple

from loguru import logger

#
# StoreGate manager
#
class StoreGate:

  #
  # Constructor
  #
  def __init__( self, 
                outputFile: str, 
                restore: bool = False 
                ) -> None:
    """
    Initialize the StoreGate instance.

    Args:
        outputFile (str): Path to the output ROOT file.
        restore (bool, optional): Whether to restore from an existing file. Defaults to False.
    """

    #outputFile = ensure_extension(outputFile,'root')
    #self.__outputFile = expand_path( outputFile )
    self.__outputFile = outputFile
    if restore:
      if not os.path.exists( self.__outputFile ):
        raise ValueError(f"File {self.__outputFile} does not exist")
      self.__file = TFile( self.__outputFile, "read")
    else:
      self.__file = TFile( self.__outputFile, "recreate")

    self.__currentDir = ""
    self.__objects    = collections.OrderedDict()
    self.__dirs       = []

    if restore:
      objs = self.restore(self.__file)
      for name, obj in objs:
        self.__dirs.append(name)
        self.__objects[name]=obj

  #
  # Get the stored file path
  #
  def local(self) -> str:
    """
    Get the stored file path.

    Returns:
        str: The path to the output ROOT file.
    """
    return self.__outputFile


  #
  # Save objects and delete storegate
  #
  def __del__(self) -> None:
    """
    Save objects and delete storegate instance.
    """
    self.__dirs = None
    self.__objects = None
    gc.collect()


  def write(self) -> None:
    """
    Write to the ROOT file and close it.
    """
    self.__file.Write()
    self.__file.Close()

  #
  # Create a folder
  #
  def mkdir(self, theDir: str) -> None:
    """
    Create a new directory in the ROOT file.

    Args:
        theDir (str): The name of the directory to create.
    """
    fullpath = (theDir).replace('//','/')    
    if not fullpath in self.__dirs:
      self.__dirs.append( fullpath )
      self.__file.mkdir(fullpath)
      self.__file.cd(fullpath)
      self.__currentDir = fullpath
      logger.debug( f'Created directory with name {theDir}')

  #
  # Go to the pointed directory
  #
  def cd(self, theDir: str) -> bool:
    """
    Change the current directory within the ROOT file.

    Args:
        theDir (str): The directory to navigate to.

    Returns:
        bool: True if navigation was successful, False otherwise.
    """
    self.__currentDir = ''
    self.__file.cd()
    fullpath = (theDir).replace('//','/')
    if fullpath in self.__dirs:
      self.__currentDir = fullpath
      if self.__file.cd(fullpath):
        return True
    logger.error( f"Couldn't cd to folder {fullpath}")
    return False


  def addHistogram( self, obj: Any ) -> None:
    """
    Add a histogram to the current directory in StoreGate.

    Args:
        obj (Any): The histogram object to add.
    """

    feature = obj.GetName()
    fullpath = (self.__currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self.__dirs:
      self.__dirs.append(fullpath)
      self.__objects[fullpath] = obj
      #obj.Write()
      logger.debug( f'Saving object type {type(obj)} into {fullpath}')


  def addObject( self, obj: Any ) -> None:
    """
    Add a ROOT object to the StoreGate, saving it immediately to the file.

    Args:
        obj (Any): The object to add.
    """

    feature = obj.GetName()
    fullpath = (self.__currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self.__dirs:
      self.__dirs.append(fullpath)
      self.__objects[fullpath] = obj
      obj.Write()
      logger.debug( f'Saving object type {type(obj)} into {fullpath}')


  def histogram(self, feature: str) -> Optional[Any]:
    """
    Retrieve a histogram or object from StoreGate by its feature path.

    Args:
        feature (str): The path or name of the feature to retrieve.

    Returns:
        Optional[Any]: The retrieved object, or None if it doesn't exist.
    """
    fullpath = (feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if fullpath in self.__dirs:
      obj = self.__objects[fullpath]
      #self._Messenger.verbose('Retrieving object type %s into %s',type(obj), fullpath)
      return obj
    else:
      logger.warning( f'Object with path {fullpath} doesnt exist')
      return None


  def getDir(self, path: str) -> Any:
    """
    Get a specific directory from the ROOT file.

    Args:
        path (str): The path of the directory.

    Returns:
        Any: The ROOT directory object.
    """
    return self.__file.GetDirectory(path)

  #
  # Use this to set labels into the histogram
  #
  def setLabels(self, feature: str, labels: List[str]) -> None:
    """
    Set bin labels for a specified histogram.

    Args:
        feature (str): The name or path of the histogram.
        labels (List[str]): A list of string labels for the bins.
    """
    histo = self.histogram(feature)
    if not histo is None:
      try:
	      if ( len(labels)>0 ):
	        for i in range( min( len(labels), histo.GetNbinsX() ) ):
	          bin = i+1;  histo.GetXaxis().SetBinLabel(bin, labels[i])
	        for i in range(histo.GetNbinsX(), min( len(labels), histo.GetNbinsX()+histo.GetNbinsY() ) ):
	          bin = i+1-histo.GetNbinsX();  histo.GetYaxis().SetBinLabel(bin, labels[i])
      except:
        logger.error( "Can not set the labels! abort.")
    else:
      logger.warning( f"Can not set the labels because this feature ({feature}) does not exist into the storage")


  def collect(self) -> None:
    """
    Clear all stored objects and directories from memory.
    """
    self.__objects.clear()
    self.__dirs = list()


  def getObjects(self) -> Dict[str, Any]:
    """
    Get all loaded objects.

    Returns:
        Dict[str, Any]: A dictionary of loaded objects with their paths as keys.
    """
    return self.__objects


  def getDirs(self) -> List[str]:
    """
    Get all tracked directories.

    Returns:
        List[str]: A list of directory paths.
    """
    return self.__dirs


  #
  # Use this method to retrieve the dirname and root object
  #
  def restore(self, d: Any, basepath: str = "/", filterDirs: Optional[List[str]] = None) -> Iterator[Tuple[str, Any]]:
    """
    Generator function to recurse into a ROOT file/dir and yield (path, obj) pairs.
    Taken from: https://root.cern.ch/phpBB3/viewtopic.php?t=11049

    Args:
        d (Any): The ROOT directory or file to start from.
        basepath (str, optional): The base path string. Defaults to "/".
        filterDirs (Optional[List[str]], optional): A list of directories to filter. Defaults to None.

    Yields:
        Iterator[Tuple[str, Any]]: A tuple containing the object's path and the object itself.
    """
    try:
      for key in d.GetListOfKeys():
        kname = key.GetName()
        if key.IsFolder():
          if filterDirs and kname not in filterDirs: 
            continue
          for i in self.restore(d.Get(kname), basepath+kname+"/"):
            yield i
        else:
          yield basepath+kname, d.Get(kname)
    except AttributeError as e:
      traceback.print_exc()
      logger.error( f"Ignore reading object of type {type(d)}.")



# helper function to retrieve the storegate using
# a root file as base.
def restoreStoreGate( ifile: str ) -> StoreGate:
  """
  Helper function to retrieve the storegate using a root file as base.

  Args:
      ifile (str): Path to the input ROOT file.

  Returns:
      StoreGate: A properly initialized StoreGate instance ready for reading.
  """
  return StoreGate( ifile, restore=True )


