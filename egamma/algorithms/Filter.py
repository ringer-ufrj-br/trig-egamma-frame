__all__ = ['Filter']


from egamma import Algorithm
from egamma import StatusCode
from egamma import StatusWTD # use this to stop the sequence and skip the event
from egamma.core.macros import *


#
# Event selection
#
class Filter( Algorithm ):

  #
  # Constructor
  #
  def __init__(self, name, filters = []):

    Algorithm.__init__(self, name)
    # Cut type and values
    self.__filters = filters


  #
  # Initialize method
  #
  def initialize(self):
    return StatusCode.SUCCESS

  
  #
  # Execute method
  #
  def execute(self, context):
    for filter in self.__filters:
      if not filter(context):
        self.wtd = StatusWTD.ENABLE
        return StatusCode.SUCCESS
    self.wtd = StatusWTD.DISABLE
    return StatusCode.SUCCESS


  #
  # Finalize method
  #
  def finalize(self):
    return StatusCode.SUCCESS






