
__all__ = ["Emulator", "attach"]


from egamma              import Algorithm
from egamma              import StatusCode
from egamma              import ToolSvc
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
    self.chains = {}


  #
  # Add a selector to the list
  #
  def __add__( self, chain ):
    self.chains[chain.name()] = chain
    return self

  #
  # Get the hypo chain
  #
  def retrieve(self, key):
    return self.chains[key] if self.isValid(key) else None



  #
  # Initialize method
  #
  def initialize(self):

    for chain in self.chains.values():
      MSG_INFO( self, f'Initializing {chain.name()} chain')
      if chain.initialize().isFailure():
        MSG_FATAL( self, f'Can not initialize {chain.name()}')

    return StatusCode.SUCCESS


  #
  # Execute method
  #
  def execute(self, context):
    return StatusCode.SUCCESS


  #
  # Accept method
  #
  def accept( self, context, key ):

    if self.isValid(key):
      return self.chains[key].accept( context )
    else:
      MSG_ERROR( self, f"The key {key} is not in the emulation" )


  #
  # Finalized method
  #
  def finalize(self):

    for chain in self.chains.values():
      MSG_INFO( self, f'Finalizing {chain.name()} chain')
      if chain.finalize().isFailure():
        MSG_ERROR( self, f'Can not finalizing {chain.name()}')

    return StatusCode.SUCCESS


  #
  # Check if the selector is installed
  #
  def isValid(self, key ):
    return True if key in self.chains.keys() else False



#
# Add the emulator chain into the chain service by default
#
ToolSvc += Emulator()



#
# Helper to avoid to much repetition code into this file
#
def attach( chains ):
  from egamma import ToolSvc
  emulator = ToolSvc.retrieve( "Emulator" )
  if type(chains) is not list:
    chains = [chains]
  names = []
  for chain in chains:
    if not emulator.isValid( chain.name() ):
      emulator+=chain
      names.append( chain.name() )
  return names

