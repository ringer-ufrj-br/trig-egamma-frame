__all__ = ["Accept"]

import collections

#
# Accept
#
class Accept:

  #
  # Constructor
  #
  def __init__(self, name, results=[] ):
    self.__name = name
    self.__results = collections.OrderedDict()

    for (key,value) in results:
      self.__results[key] = value

    self.__decoration = {}

  #
  # Get the accept name
  #
  def name(self):
    return self.__name


  #
  # Add new cut
  #
  def addCut( self, key ):
    self.__results[key] = False


  #
  # Set cut result value
  #
  def setCutResult( self, key, value ):
    self.__results[key] = value


  #
  # Get cut result value
  #
  def getCutResult( self, key ):
    try:
      return self.__results[key]
    except KeyError as e:
      print( e )


  #
  # Is passed
  #
  def __bool__(self):
    x = [v for _, v in self.__results.items()]
    return all( [value for _, value in self.__results.items()] )

  #
  # Add decoration
  #
  def setDecor( self, key, value ):
    self.__decoration[key] = value

  #
  # Get decoration
  #
  def getDecor( self, key ):
    return self.__decoration[key]




from . import Emulator
__all__.extend(Emulator.__all__)
from .Emulator import *


from . import run3
__all__.extend(run3.__all__)
from .run3 import *

