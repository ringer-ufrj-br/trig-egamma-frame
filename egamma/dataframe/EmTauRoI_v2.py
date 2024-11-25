
__all__ = ['EmTauRoI_v2']

from egamma.core import EDM
from egamma.core import StatusCode
from egamma.core import stdvector2list



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


    def __init__(self):
        EDM.__init__(self)


    def initialize(self):
      """
        Link all branches
      """
      self.link(self.__eventBranches)
      return StatusCode.SUCCESS
      

    def wstot(self):
        """
          Retrieve the L1 wstot information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_wstot
        

    def reta(self):
        """
          Retrieve the L1 reta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_reta
       

    def rhad(self):
        """
          Retrieve the L1 rhad information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_rhad
   

    def roi_et(self):
        """
          Retrieve the L1 roi_et information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_roi_et
      

    def eta(self):
        """
          Retrieve the eta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_eta
    

    def phi(self):
        """
        Retrieve the phi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L1eFex_el_phi
     




