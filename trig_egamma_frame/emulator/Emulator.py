
__all__ = ["Emulator", "attach"]


from loguru import logger
from trig_egamma_frame import Algorithm, StatusCode, ToolSvc
import collections


class Emulator( Algorithm ):
  """
  The Emulator class is an Algorithm designed to manage and execute multiple
  emulation chains. It provides methods to register, retrieve, and evaluate 
  acceptance for different chains.
  """


  def __init__(self):
    """
    Initialize the Emulator algorithm and the internal storage for chains.
    """
    Algorithm.__init__(self, "Emulator") 
    self.chains = {}


  def __add__( self, chain  ):
    """
    Add an emulation chain to the emulator.

    Args:
        chain: The chain object to be added. Must provide a name() method.
    
    Returns:
        Emulator: Returns the instance itself to allow chaining (e.g., emulator += chain).
    """
    self.chains[chain.name()] = chain
    return self

  def retrieve(self, key):
    """
    Retrieve a registered chain by its key (name).

    Args:
        key (str): The name of the chain to retrieve.

    Returns:
        The chain object if found and valid; otherwise None.
    """
    return self.chains[key] if self.isValid(key) else None



  def initialize(self) -> StatusCode:
    """
    Initialize all registered emulation chains.

    Returns:
        StatusCode: SUCCESS if all chains were successfully initialized, FAILURE otherwise.
    """

    for chain in self.chains.values():
      logger.info( f'Initializing {chain.name()} chain')
      if chain.initialize().isFailure():
        logger.error( f'Can not initialize {chain.name()}')

    return StatusCode.SUCCESS


  def execute(self, context) -> StatusCode:
    """
    Execute the algorithm for a given context. Currently returns SUCCESS by default.

    Args:
        context: The execution context (e.g., event store).

    Returns:
        StatusCode: Always returns SUCCESS.
    """
    return StatusCode.SUCCESS


  def accept( self, context, key ):
    """
    Check if the specified chain accepts the current context.

    Args:
        context: The execution context.
        key (str): The name of the chain to evaluate.

    Returns:
        The result of the chain's accept method if valid; otherwise logs an error.
    """

    if self.isValid(key):
      return self.chains[key].accept( context )
    else:
      logger.error( f"The key {key} is not in the emulation" )


  def finalize(self) -> StatusCode:
    """
    Finalize all registered emulation chains.

    Returns:
        StatusCode: SUCCESS if all chains were successfully finalized, FAILURE otherwise.
    """

    for chain in self.chains.values():
      logger.info( f'Finalizing {chain.name()} chain')
      if chain.finalize().isFailure():
        logger.error( f'Can not finalizing {chain.name()}')

    return StatusCode.SUCCESS


  def isValid(self, key ):
    """
    Check if a chain with the given key is registered in the emulator.

    Args:
        key (str): The name of the chain to check.

    Returns:
        bool: True if the key is found in registered chains, False otherwise.
    """
    return True if key in self.chains.keys() else False



#
# Add the emulator chain into the chain service by default
#
ToolSvc += Emulator()



def attach( chains ):
  """
  Helper function to attach one or multiple chains to the default Emulator tool service.

  Args:
      chains: A single chain object or a list of chain objects to attach.

  Returns:
      list: A list of names of the chains that were successfully attached.
  """
  from trig_egamma_frame import ToolSvc
  emulator = ToolSvc.retrieve( "Emulator" )
  if type(chains) is not list:
    chains = [chains]
  names = []
  for chain in chains:
    if not emulator.isValid( chain.name() ):
      emulator+=chain
      names.append( chain.name() )
  return names

