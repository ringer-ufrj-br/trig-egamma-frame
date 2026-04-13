__all__ = ['Filter']


from trig_egamma_frame.kernel import Algorithm, StatusCode, StatusWTD, EventContext
from trig_egamma_frame import logger

#
# Event selection
#
class Filter( Algorithm ):

  
  def __init__(self, name, filters = []):

    Algorithm.__init__(self, name)
    # Cut type and values
    self.__filters = filters


  def initialize(self) -> StatusCode:
    return StatusCode.SUCCESS


  def execute(self, context: EventContext) -> StatusCode:
    for filter in self.__filters:
      if not filter(context):
        logger.info(f"Filter failed")
        self.wtd = StatusWTD.ENABLE
        return StatusCode.SUCCESS
    self.wtd = StatusWTD.DISABLE
    return StatusCode.SUCCESS


  def finalize(self) -> StatusCode:
    return StatusCode.SUCCESS






