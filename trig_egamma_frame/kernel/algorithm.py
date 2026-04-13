
__all__ = [
  'Algorithm', 
  'EventContext', 
  'StatusTool', 
  'StatusWTD', 
  'StatusCode', 
  'ToolSvc', 
  'ToolMgr'
]

import ROOT
import collections
from enum          import Enum
from trig_egamma_frame import logger
from typing        import Any, List
from .StoreGate import StoreGate
from trig_egamma_frame.enumerators import DataframeSchemma




class StatusTool(Enum):
  """
    The status of the tool
  """
  IS_FINALIZED   = 3
  IS_INITIALIZED = 2 
  ENABLE  = 1
  DISABLE = -1
  NOT_INITIALIZED = -2
  NOT_FINALIZED = -3
 

# Watch dog status
class StatusWTD(Enum):
  """
    Use this to enable or disable the tool in execute call
  """
  ENABLE  = 1
  DISABLE = 0



# Status code object used for error code
class StatusObj:

  _status = 1

  def __init__(self, sc):
    self._status = sc

  def isFailure(self):
    """
    Check if the status code is a failure

    Returns:
      bool: True if the status code is a failure, False otherwise
    """
    if self._status < 1:
      return True
    else:
      return False

  def __eq__(self, a, b):
    """
    Check if the status code is equal to another status code

    Args:
      a (StatusObj): The first status code
      b (StatusObj): The second status code

    Returns:
      bool: True if the status code is equal to another status code, False otherwise
    """
    if a.status == b.status:
      return True
    else:
      return False

  def __ne__(self, a, b):
    """
    Check if the status code is not equal to another status code

    Args:
      a (StatusObj): The first status code
      b (StatusObj): The second status code

    Returns:
      bool: True if the status code is not equal to another status code, False otherwise
    """
    if a.status != b.status:
      return True
    else:
      return False

  @property
  def status(self):
    """
    Get the status code

    Returns:
      int: The status code
    """
    return self._status




# status code enumeration
class StatusCode:
  """
    The status code of something
  """
  SUCCESS = StatusObj(1)
  FAILURE = StatusObj(0)
  FATAL   = StatusObj(-1)



class EventContext:

  def __init__(self, t : ROOT.TTree):
    """
    Initialize the event context

    Args:
      t (ROOT.TTree): The tree to use for the event context
    """
    self._containers = collections.OrderedDict()
    self._tree=None
    self._decorations = collections.OrderedDict()
    self._current_entry=None
    self._tree = t


  def setHandler(self, key : str, obj : Any):
    """
    Set the handler for a given key

    Args:
      key (str): The key to set the handler for
      obj (Any): The handler to set for the given key

    Returns:
      None
    """
    if key in self._containers.keys():
      logger.error( f"Key {key} exist into the event context. Attach is not possible..." )
    else:
      self._containers[key]=obj

  def getHandler(self,key : str) -> Any:
    """
    Get the handler for a given key

    Args:
      key (str): The key to get the handler for

    Returns:
      Any: The handler for the given key
    """
    return None if not key in self._containers.keys() else self._containers[key]

  def getEntries(self) -> int:
    """
    Get the number of entries in the tree

    Returns:
      int: The number of entries in the tree
    """
    return self._tree.GetEntries()

  def setEntry(self,entry : int):
    """
    Set the current entry

    Args:
      entry (int): The entry to set

    Returns:
      None
    """
    self._current_entry=entry

  def getEntry(self) -> int:
    """
    Get the current entry

    Returns:
      int: The current entry
    """
    return self._current_entry

  def execute(self) -> StatusCode:
    """
    Execute the event context

    Returns:
      StatusCode: The status code of the execution
    """
    self._tree.GetEntry( self.getEntry() )
    for key, edm in self._containers.items():
      if edm.execute().isFailure():
        logger.warning( f"Can not execute the edm {key}" )
    return StatusCode.SUCCESS

  def initialize(self) -> StatusCode:
    """
    Initialize the event context

    Returns:
      StatusCode: The status code of the initialization
    """
    return StatusCode.SUCCESS

  def finalize(self) -> StatusCode:
    """
    Finalize the event context

    Returns:
      StatusCode: The status code of the finalization
    """
    return StatusCode.SUCCESS

  def setDecor(self, key : str, v : Any):
    """
    Set the decoration for a given key

    Args:
      key (str): The key to set the decoration for
      v (Any): The decoration to set for the given key

    Returns:
      None
    """
    self._decoration[key] = v

  def getDecor(self,key : str) -> Any:
    """
    Get the decoration for a given key

    Args:
      key (str): The key to get the decoration for

    Returns:
      Any: The decoration for the given key
    """
    try:
      return self._decoration[key]
    except KeyError:
      logger.error( f"Decoration {key} not found" )

  def clearDecorations(self):
    """
    Clear all decorations

    Returns:
      None
    """
    self._decoration.clear()

  def decorations(self) -> List[str]:
    """
    Get all decorations

    Returns:
      List[str]: The list of decorations
    """
    return self._decoration.keys()



class Service:

  def __init__(self, name : str):
    """
    Initialize the service

    Args:
      name (str): The name of the service
    """
    self.__name = name
    self.__tools = collections.OrderedDict()

  @property
  def name(self) -> str:
    """
    Get the name of the service

    Returns:
      str: The name of the service
    """
    return self.__name

  def get(self, name : str) -> Any:
    """
    Get the tool for a given name

    Args:
      name (str): The name of the tool to get

    Returns:
      Any: The tool for the given name
    """
    return self.__tools[name]

  def put(self, tool : Any):
    """
    Put the tool in the service

    Args:
      tool (Any): The tool to put in the service

    Returns:
      None
    """
    self.__tools[ tool.name() ] =  tool

  def __iter__(self):
    """
    Iterate over the tools in the service

    Yields:
      Any: The tool in the service
    """
    for name, tool in self.__tools.items():
      yield tool

  def push_back(self, tool : Any):
    """
    Push the tool to the back of the service

    Args:
      tool (Any): The tool to push to the back of the service

    Returns:
      None
    """
    self.__tools[ tool.name() ] = tool

  def __add__(self, tool : Any):
    """
    Add the tool to the service

    Args:
      tool (Any): The tool to add to the service

    Returns:
      Any: The service with the tool added
    """
    self.__tools[ tool.name() ] =  tool
    return self

  def clear(self):
    """
    Clear all tools from the service

    Returns:
      None
    """
    self.__tools.clear()

  def __len__(self) -> int:
    """
    Get the number of tools in the service

    Returns:
      int: The number of tools in the service
    """
    return len(self.__tools)

  def __str__(self):
    """
    Return a string representation of the service

    Returns:
      str: The string representation of the service
    """ 
    logger.info( f"service: {self.name()}")
    for name, tool in self._tools.items():
      logger.info( f"  {tool.name()}")

  def get_tools(self):
    """
    Get all tools in the service

    Returns:
      List[Any]: The list of tools in the service
    """
    return self.__tools.values()

  def retrieve( self, key : str ) -> Any:
    """
    Retrieve the tool for a given key

    Args:
      key (str): The key to retrieve the tool for

    Returns:
      Any: The tool for the given key
    """
    if key in self.__tools.keys():
      return self.__tools[key]
    else:
      logger.error( f"tool with name {key} not found in the tool service")




# Use this to attach all tools
ToolSvc = Service("ToolSvc")

# Use this to attach all event loop manager
ToolMgr = Service("ToolMgr")





#
# Base class used for all tools for this framework
#
class Algorithm:
  """Base class used for all tools for this framework."""

  def __init__(self, name : str):
    """
      Initialize the Algorithm with a custom name and default state flags.

      Args:
        name (str): The name of the algorithm.
    """
    self._name          = name
    self._wtd           = StatusWTD.DISABLE
    self._status        = StatusTool.ENABLE
    self._initialized   = StatusTool.NOT_INITIALIZED
    self._finalized     = StatusTool.NOT_FINALIZED
 

  def name(self) -> str:
    """Retrieve the explicit name of the algorithm."""
    return self._name

  @property
  def dataframe(self) -> DataframeSchemma:
    """Property to access the dataframe."""
    return self._dataframe

  @dataframe.setter
  def dataframe(self,v):
    """Setter for the dataframe property."""
    self._dataframe = v

  def setContext( self, context : EventContext):
    """Set the active EventContext for this algorithm execution."""
    self._context = context

  def getContext(self) -> EventContext:
    """Get the active EventContext."""
    return self._context

  def setStoreGateSvc(self,sg : StoreGate):
    """Set the StoreGate service instance used by this algorithm."""
    self._storegateSvc=sg

  def getStoreGateSvc(self) -> StoreGate:
    """Get the StoreGate service instance."""
    return self._storegateSvc

  @property
  def storeSvc(self) -> StoreGate:
    """Property to safely retrieve the StoreGate service. Fatals out if missing."""
    if self._storegateSvc is not None:
      return self._storegateSvc
    else:
      raise ValueError(  "Attempted to access storeSvc which wasn't set.")

  @storeSvc.setter
  def storeSvc(self, s):
    """Setter to assign the StoreGate service, ensuring type safety."""
    if not isinstance(s, StoreGate):
      raise ValueError( "Attempted to set StoreGate to instance of non StoreGate type")
    self._storegateSvc=s

  def initialize(self) -> StatusCode:
    """Initialize the algorithm component. Expected to be overridden by derived classes."""
    return StatusCode.SUCCESS

  def execute(self, context : EventContext) -> StatusCode:
    """Main execution block of the algorithm per-event."""
    self.setContext(context)
    self._wtd = StatusWTD.DISABLE
    return StatusCode.SUCCESS

  def finalize(self) -> StatusCode:
    """Finalize the algorithm execution, free up resources if necessary."""
    return StatusCode.SUCCESS

  @property
  def wtd(self) -> StatusWTD:
    """Retrieve the watch dog status."""
    return self._wtd

  @wtd.setter
  def wtd(self, v : StatusWTD):
    """Set and enforce the watch dog status value."""
    self._wtd = v

  @property
  def status(self) -> StatusTool:
    """Retrieve the enable/disable status of the algorithm."""
    return self._status

  def disable(self) -> None:
    """Disable this algorithm from regular execution loop."""
    logger.info( f'disable {self._name} tool service.')
    self._status = StatusTool.DISABLE

  def enable(self) -> None:
    """Enable this algorithm for normal execution."""
    logger.info( f'enable {self._name} tool service.')
    self._status = StatusTool.ENABLE

  def init_lock(self) -> None:
    """Lock the initialization state flag to True/IS_INITIALIZED."""
    self._initialized = StatusTool.IS_INITIALIZED

  def fina_lock(self) -> None:
    """Lock the finalized state flag to True/IS_FINALIZED."""
    self._finalized = StatusTool.IS_FINALIZED

  def isInitialized(self) -> bool:
    """Check if the internal lock signals the algorithm is fully initialized."""
    return self._initialized is StatusTool.IS_INITIALIZED

  def isFinalized(self) -> bool:
    """Check if the internal lock signals the algorithm is fully finalized."""
    return self._finalized is StatusTool.IS_FINALIZED 
    
    