

__all__ = ["ToolSvc", "ToolMgr"]

from trig_egamma_frame              import Messenger
from trig_egamma_frame.core.macros  import *
import collections


class Service( Messenger ):

  def __init__(self, name):
    Messenger.__init__(self)
    self._name = name
    self._tools = collections.OrderedDict()

  def name(self):
    return self._name

  def get(self, name):
    return self._tools[name]

  def put(self, tool):
    self._tools[ tool.name() ] =  tool

  def __iter__(self):
    for name, tool in self._tools.items():
      yield tool

  def disable(self):
    for name, tool in self._tools.items():
      MSG_DEBUG( self, f"Disable {name} tool")
      tool.disable()

  def enable(self):
    for name, tool in self._tools.items():
      MSG_DEBUG( self, f"Enable {name} tool")
      tool.enable()

  def push_back(self, tool):
    self._tools[ tool.name() ] = tool

  def __add__(self, tool):
    self._tools[ tool.name() ] =  tool
    return self

  def clear(self):
    self._tools.clear()

  def resume(self):
    MSG_INFO( self, "Service: %s", self.name())
    for name, tool in self._tools.items():
      MSG_INFO( self, " * %s as tool", tool.name())

  def getTools(self):
    return [ tool for _, tool in self._tools.items() ]

  def retrieve( self, key ):
    if key in self._tools.keys():
      return self._tools[key]
    else:
      MSG_ERROR( self, f"Tool with name {key} not found in the tool service")


#
# Create tool services
#


# Use this to attach all tools
ToolSvc = Service("ToolSvc")

# Use this to attach all event loop manager
ToolMgr = Service("ToolMgr")




