
__all__ = ["Emulator"]


from egamma              import Algorithm
from egamma              import StatusCode
from egamma.core.macros  import *
import collections


#
# Emulator
#
class Emulator( Algorithm ):


  #
  # Constructor
  #
  def __init__(self):
    Algorithm.__init__(self, "Emulator") 
    self.__chains = {}


  #
  # Add a selector to the list
  #
  def __add__( self, chain ):
    self.__chains[chain.name()] = chain
    return self


  #
  # Initialize method
  #
  def initialize(self):

    for chain in self.__chains.values():
      MSG_INFO( self, f'Initializing {chain.name()} chain')
      if chain.initialize().isFailure():
        MSG_FATAL( self, 'Can not initialize %s',chain.name())

    return StatusCode.SUCCESS


  #
  # Execute method
  #
  def execute(self, context):

    for chain in self.__chains.values():
      chain.emulate(context)

    return StatusCode.SUCCESS



  #
  # Finalized method
  #
  def finalize(self):

    for chain in self.__chains.values():
      MSG_INFO( self, f'Finalizing {chain.name()} chain')
      if chain.finalize().isFailure():
        MSG_FATAL( self, f'Can not finalizing {chain.name()}')

    return StatusCode.SUCCESS


  #
  # Check if the selector is installed
  #
  def isValid(self, key ):
    return True if key in self.__chains.keys() else False




