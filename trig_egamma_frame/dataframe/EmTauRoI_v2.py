
__all__ = ['EmTauRoI_v2']

from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode

class EmTauRoI_v2(EDM):

    __eventBranches = [
                'trig_L1eFex_el_eta',
                'trig_L1eFex_el_phi',
                'trig_L1eFex_el_roi_et',
                'trig_L1eFex_el_wstot',
                'trig_L1eFex_el_reta',
                'trig_L1eFex_el_rhad'
                #'trig_L1eFex_el_emClus',
                #'trig_L1eFex_el_tauClus',
                #'trig_L1eFex_el_emIso',
                #'trig_L1eFex_el_hadCore',
                ]


    def __init__(self) -> None:
        """
          Initialize the EmTauRoI_v2 object.
        """
        EDM.__init__(self)


    def initialize(self) -> StatusCode:
      """
        Link all branches
      """
      self.link(self.__eventBranches)
      return StatusCode.SUCCESS
      

    def wstot(self) -> float:
        """
          Retrieve the L1 wstot information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_wstot
        

    def reta(self) -> float:
        """
          Retrieve the L1 reta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_reta
       

    def rhad(self) -> float:
        """
          Retrieve the L1 rhad information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_rhad
   

    def roi_et(self) -> float:
        """
          Retrieve the L1 roi_et information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_roi_et
      

    def eta(self) -> float:
        """
          Retrieve the eta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_eta
    

    def phi(self) -> float:
        """
        Retrieve the phi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_phi
     




