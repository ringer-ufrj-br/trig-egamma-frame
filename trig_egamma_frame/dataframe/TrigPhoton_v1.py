
__all__ = ['TrigPhoton_v1']

from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode
import numpy as np

class TrigPhoton_v1(EDM):

    __eventBranches = [
                      'trig_L2_ph_pt',
                      'trig_L2_ph_caloEta',
                      'trig_L2_ph_eta',
                      'trig_L2_ph_phi',
                      'trig_L2_ph_nTRTHits',
                      'trig_L2_ph_nTRTHiThresholdHits',
                      'trig_L2_ph_etOverPt',
                    ]
                

    def __init__(self):
        EDM.__init__(self)


    def initialize(self) -> StatusCode:
        """
          Initialize all branches
        """
        self.link( self.__eventBranches )
        return StatusCode.SUCCESS
    



    def pt(self) -> float:
        """
          Retrieve the pt information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_pt[self.getPos()]
       


    def eta(self) -> float:
        """
        Retrieve the eta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_eta[self.getPos()]
        

    def phi(self) -> float:
        """
        Retrieve the phi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_phi[self.getPos()]
        

    def caloEta(self) -> float:
        """
        Retrieve the caloEta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_caloEta[self.getPos()]
        

    def numberOfTRTHits(self) -> int:
        """
        Retrieve the number of TRT hits information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_nTRTHits[self.getPos()]
        

    def numberOfTRTHiThresholdHits(self) -> int:
        """
        Retrieve the number of TRT high thresholdhits information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_nTRTHiThresholdHits[self.getPos()]
        

    def etOverPt(self) -> float:
        """
        Retrieve the et/pt information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_ph_etOverPt[self.getPos()]
        

    def size(self) -> int:
        return self._event.trig_L2_el_pt.size()



    def setToBeClosestThanCluster( self ) -> None:
      idx = 0; minDeltaR = 999
      for trk in self:
        dR = self.deltaR( 0.0, 0.0, trk.trkClusDeta(), trk.trkClusDphi() )
        if dR < minDeltaR:
          minDeltaR = dR
          idx = self.getPos()
      self.setPos(idx)


    def deltaR( self, eta1: float, phi1: float, eta2: float, phi2: float ) -> float:
      deta = abs( eta1 - eta2 )
      dphi = abs( phi1 - phi2 ) if abs(phi1 - phi2) < np.pi else (2*np.pi-abs(phi1-phi2))
      return np.sqrt( deta*deta + dphi*dphi )




