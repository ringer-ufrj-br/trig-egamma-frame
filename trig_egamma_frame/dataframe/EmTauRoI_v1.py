
__all__ = ['EmTauRoI_v1']


from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode

class EmTauRoI_v1(EDM):

    __eventBranches = [
                'trig_L1_eta',
                'trig_L1_phi',
                'trig_L1_emClus',
                'trig_L1_tauClus',
                'trig_L1_emIsol',
                'trig_L1_hadIsol',
                ]


    def __init__(self):
        EDM.__init__(self)


    def initialize(self) -> StatusCode:
      """
        Link all branches
      """
      self.link(self.__eventBranches)
      return StatusCode.SUCCESS
      

    def emClus(self) -> float:
        """
          Retrieve the L1 EmClus information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_emClus
        

    def tauClus(self) -> float:
        """
          Retrieve the L1 tauClus information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_tauClus
       

    def emIsol(self) -> float:
        """
          Retrieve the L1 emIsol information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_emIsol
   

    def hadCore(self) -> float:
        """
          Retrieve the L1 hadIsol information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_hadIsol
      

    def eta(self) -> float:
        """
          Retrieve the eta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_eta
    

    def phi(self) -> float:
        """
        Retrieve the phi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1_phi
     




