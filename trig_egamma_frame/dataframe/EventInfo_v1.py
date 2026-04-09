
__all__ = ['EventInfo_v1']

from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode


class EventInfo_v1(EDM):
    __eventBranches = [
            'RunNumber',
            'avgmu',
            'LumiBlock',
            #'el_nPileupPrimaryVtx'
            ]


    def __init__(self):
        EDM.__init__(self)


    def initialize(self) -> StatusCode:
        """
          Link all branches
        """
        self.link( self.__eventBranches )
        return StatusCode.SUCCESS


    def nvtx(self) -> int:
        """
          Retrieve the Nvtx information from Physval or SkimmedNtuple
        """
        return self._event.el_nPileupPrimaryVtx
   

   
    def avgmu(self) -> float:
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.avgmu
        

    def RunNumber(self) -> int:
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.RunNumber
        

    def LumiBlock(self) -> int:
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.LumiBlock
        

    def MCPileupWeight(self) -> float:
        """
          Retrieve the Pileup Weight information from Physval or SkimmedNtuple
        """
        return 1
        

    def id(self) -> int:
        return self._id

    def setId(self, v: int):
        self._id = v





