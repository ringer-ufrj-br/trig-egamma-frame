
__all__ = ['MonteCarlo_v2']

from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode


class MonteCarlo_v2(EDM):

  __eventBranches = [ # For electron and photon
                      'mc_hasMC',
                      'mc_isTruthElectronAny',
                      'mc_isTruthElectronFromZ',
                      #'mc_isTruthElectronFromW',
                      'mc_isTruthElectronFromJpsiPrompt',
                      #'mc_isTruthJetFromAny',
                      #'mc_isTruthPhotonFromAny',
                      'mc_type',
                      'mc_origin',
                    ]


  def __init__(self) -> None:
    """
    Initialize the MonteCarlo_v2 object
    """
    EDM.__init__(self)



  def initialize(self) -> StatusCode:
    """
    Initialize all branches
    """
    self.link( self.__eventBranches )
    return StatusCode.SUCCESS


  def isTruthElectronFromZ(self) -> bool:
    """
    Retrieve whether true electron is from Z
    """
    return self._event.mc_isTruthElectronFromZ
   

  def isTruthElectronFromW(self) -> bool:
    """
    Retrieve whether true electron is from W
    """
    return self._event.mc_isTruthElectronFromW
    

  def isTruthElectronFromJpsiPrompt(self) -> bool:
    """
    Retrieve whether true electron is from JpsiPrompt
    """
    return self._event.mc_isTruthElectronFromJpsiPrompt
   

  def isTruthElectronFromAny(self) -> bool:
    """
    Retrieve whether true electron is from Any
    """
    return self._event.mc_isTruthElectronAny
    

  def isTruthJetFromAny(self) -> bool:
    """
    Retrieve whether true jet is from Any
    """
    return self._event.mc_isTruthJetFromAny
   

  def isTruthPhotonFromAny(self) -> bool:
    """
    Retrieve whether true photon is from Any
    """
    return self._event.mc_isTruthPhotonFromAny
   
  
  def isMC(self) -> bool:
    """
      Retrieve the isMC information
    """
    return bool(self._event.mc_hasMC)
   

  def type(self) -> int:
    """
      Retrieve the MC type information
    """
    return self._event.mc_type
    

  def origin(self) -> int:
    """
      Retrieve the MC origin information
    """
    return self._event.mc_origin
    


