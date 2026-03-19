
__all__ = ['EDM']

from egamma.kernel import StatusCode
from typing import Any, List
from loguru import logger
from cppyy.ll import cast
import traceback
import ROOT



class EDM:

  # set the default skimmed dataframe
  _dataframe = None
  
  def __init__(self):

    """
    Initialize the Event Data Model (EDM) base class.

    This class provides the foundational interface for managing event data,
    including tracking the current dataframe, ROOT trees, and event context.
    It maintains internal states for:
    - Event iteration index (`_idx`) and HLT (High-Level Trigger) flags (`_is_hlt`).
    - Additional event decorations (`_decoration`).
    - The underlying ROOT tree (`_tree`) and the event object (`_event`).
    - Execution context (`_context`) and metadata parameters (`_metadataParams`).
    - The list of active branches linked to the body class (`_branches`).
    """
    
    self._idx = 0
    self._is_hlt = False
    self._decoration = dict()
    self._tree  = None
    self._event = None
    self._context = None
    # this is used for metadata properties
    self._useMetadataParams = False
    self._metadataParams = {}
    self._branches = list() # hold all branches from the body class


  def setContext( self, context):
    self._context=context

  def getContext(self) :
    return self._context

  def initialize(self):
    return StatusCode.SUCCESS

  def execute(self) -> StatusCode:
    return StatusCode.SUCCESS

  def finalize(self) -> StatusCode:
    return StatusCode.SUCCESS

  @property
  def dataframe(self):
    return self._dataframe

  @dataframe.setter
  def dataframe(self, v):
    self._dataframe=v

  @property
  def tree(self) -> ROOT.TTree:
    self._tree

  @tree.setter
  def tree(self, v : ROOT.TTree):
    self._tree = v

  @property
  def event(self):
    return self._event

  @event.setter 
  def event(self, v):
    self._event = v

  def setDecor(self, key : str, v : Any):
    self._decoration[key] = v

  def getDecor(self,key : str) -> Any:
    try:
      return self._decoration[key]
    except KeyError:
      self._logger.warning('Decoration %s not found',key)

  def clearDecorations(self):
    self._decoration = dict()

  def decorations(self) -> List[str]:
    return self._decoration.keys()

  def setBranchAddress( self, tree : ROOT.TTree, varname : str, holder : Any, pointername : str = None):
    """
    Set the branch address for a given variable.

    Args:
      tree (ROOT.TTree): The ROOT tree to set the branch address on.
      varname (str): The name of the variable to set the branch address for.
      holder (Any): The holder for the branch address.
      pointername (str, optional): The name of the pointer. Defaults to None.
    """
    if not pointername:  pointername=varname
    " Set tree branch varname to holder "
    if not tree.GetBranchStatus(varname):
      tree.SetBranchStatus( varname, True )
      if ROOT.gROOT.GetVersion()<'6.22':
        tree.SetBranchAddress( varname, ROOT.AddressOf(holder, pointername) )
      else:
        tree.SetBranchAddress( varname, cast['void*'](ROOT.addressof(holder, pointername)) )
      logger.debug( f"Set {varname} branch address on {tree}" )
    else:
      logger.warning( f"Already set {varname} branch address on {tree}" )


  def retrieve(self, key : str):
    """
    Retrieve a container from the EDM.

    Args:
      key (str): The name of the container to retrieve.

    Returns:
      Any: The container with the given name.
    """
    try:
      return self._containersSvc[key]
    except KeyError:
      logger.warning( f"container with name {key} not found in the tool service")


  def useMetadataParams(self):
    return self._useMetadataParams

  def setMetadataParams( self, dParam ):
    self._metadataParams = dParam

  def checkBody(self, branch : str) -> bool:
    """
    Check if the branch belongs to the body class.

    Args:
      branch (str): The name of the branch to check.

    Returns:
      bool: True if the branch belongs to the body class, False otherwise.
    """
    if branch in self._branches:
      return True
    elif branch in self.decorations():
      return True
    else:
      return False


  def accept(self, v):
    return True


  # special methos for cern/atlas project
  @property
  def is_hlt(self):
    return self._is_hlt

  # special methos for cern/atlas project
  @is_hlt.setter
  def is_hlt(self, v):
    self._is_hlt=v


  # special methos for cern/atlas project
  def __iter__(self):
    self.setPos(-1) # force to be -1 
    if self.size()>0:
      while (self.getPos()+1) < self.size():
        self.setPos(self.getPos()+1)
        yield self

  # special methos for cern/atlas project
  def size(self):
    return 1

  # special methos for cern/atlas project
  def setPos( self, idx ):
    self._idx = idx

  # special methos for cern/atlas project
  def getPos( self ):
    return self._idx


  #
  # Link
  #
  def link( self, branches ):
    # loop over branches
    for branch in branches:
        try:
            self.setBranchAddress( self._tree, branch  , self._event)
            self._branches.append(branch) # hold all branches from the body class
        except Exception as e:
            traceback.print_exc()
            print(e)
            logger.warning( f"tt's not possible to set this branche: {branch}" )





