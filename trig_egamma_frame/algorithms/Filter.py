__all__ = [
    'Filter',        
    ]

import numpy as np

from trig_egamma_frame.kernel import Algorithm, StatusCode, StatusWTD, EventContext
from trig_egamma_frame import logger, GeV

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




class EventFilter:
    def __init__ ( self, 
                  is_data : bool=False, 
                  is_background : bool=False
                  ):
        self.is_data = is_data
        self.is_background = is_background

    def __call__(self, ctx : EventContext) -> bool:

        elCont = ctx.getHandler( "ElectronContainer" )
        if elCont.et() < 2*GeV:
            return False
        fc = ctx.getHandler( "HLT__TrigEMClusterContainer" )
        if not fc.isGoodRinger():
            return False

        if self.is_data:
            return True
        
        mc = ctx.getHandler("MonteCarloContainer")
        if self.is_background:
            if mc.isTruthElectronFromAny():
                return False
        else:
            if fc.et() < 15*GeV: # Jpsiee
                if not mc.isTruthElectronFromJpsiPrompt():
                    return False
            else: # Zee
                if not mc.isTruthElectronFromZ():
                    return False

        return True

def isZ_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromZ())
def isAny_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromAny())
def isJpsi_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromJpsiPrompt())

    




