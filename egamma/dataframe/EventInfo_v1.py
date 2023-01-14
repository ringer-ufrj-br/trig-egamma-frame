
__all__ = ['EventInfo_v1']

from trig_egamma_frame.core import EDM
from trig_egamma_frame.core import StatusCode


class EventInfo_v1(EDM):
    __eventBranches = [
            'RunNumber',
            'avgmu',
            'LumiBlock',
            #'el_nPileupPrimaryVtx'
            ],

            


    def __init__(self):
        EDM.__init__(self)


    def initialize(self):
        """
          Link all branches
        """
        self.link( self.__eventBranches )
        return StatusCode.SUCCESS


    def nvtx(self):
        """
          Retrieve the Nvtx information from Physval or SkimmedNtuple
        """
        return self._event.el_nPileupPrimaryVtx
   

   
    def avgmu(self):
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.avgmu
        

    def RunNumber(self):
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.RunNumber
        

    def LumiBlock(self):
        """
          Retrieve the avgmu information from Physval or SkimmedNtuple
        """
        return self._event.LumiBlock
        

    def MCPileupWeight(self):
        """
          Retrieve the Pileup Weight information from Physval or SkimmedNtuple
        """
        return 1
        

    def id(self):
        return self._id

    def setId(self, v):
        self._id = v





