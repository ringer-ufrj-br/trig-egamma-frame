
__all__ = ['TrigElectron_v2']

from trig_egamma_frame.kernel import EDM
from trig_egamma_frame import StatusCode
import numpy as np


class TrigElectron_v2(EDM):

    __eventBranches = [
                      'trig_L2_el_pt',
                      #'trig_L2_el_caloEta',
                      'trig_L2_el_eta',
                      'trig_L2_el_phi',
                      #'trig_L2_el_charge',
                      'trig_L2_el_etOverPt',
                      'trig_L2_el_trkClusDeta',
                      'trig_L2_el_trkClusDphi',
                      'trig_L2_el_trk_d0',
                      #'trig_L2_el_nTRTHits',
                      #'trig_L2_el_nTRTHiThresholdHits',
                    ]
                

    def __init__(self) -> None:
        """
          Initialize the TrigElectron_v2 object
        """
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
        return self._event.trig_L2_el_pt[self.getPos()]
        

    def eta(self) -> float:
        """
        Retrieve the eta information from Physval or SkimmedNtuple
        """            
        return self._event.trig_L2_el_eta[self.getPos()]
        

    def phi(self) -> float:
        """
        Retrieve the phi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_phi[self.getPos()]
      
      
    #def charge(self):
    #    """
    #     Retrieve the charge information from Physval or SkimmedNtuple
    #    """
    #    return self._event.trig_L2_el_charge[self.getPos()]
       

    def caloEta(self) -> float:
        """
        Retrieve the caloEta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_caloEta[self.getPos()]
      

    def etOverPt(self) -> float:
        """
        Retrieve the et/pt information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_etOverPt[self.getPos()]
       

    def trkClusDeta(self) -> float:
        """
        Retrieve the trkClusDeta information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_trkClusDeta[self.getPos()]
        

    def trkClusDphi(self) -> float:
        """
        Retrieve the trkClusDphi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_trkClusDphi[self.getPos()]
        

    def d0(self) -> float:
        """
        Retrieve the trkClusDphi information from Physval or SkimmedNtuple
        """
        return self._event.trig_L2_el_trk_d0[self.getPos()]
        

    def numberOfTRTHits(self) -> int:
        """
        Retrieve the number of TRT hits information from Physval or SkimmedNtuple
        """
        return -1
        

    def numberOfTRTHiThresholdHits(self) -> int:
        """
        Retrieve the number of TRT high thresholdhits information from Physval or SkimmedNtuple
        """
        return -1

    def size(self) -> int:
        """
        Retrieve the container size
        """
        return self._event.trig_L2_el_pt.size()



    def setToBeClosestThanCluster( self ) -> None:
      """
      Set the position to be the closest to the cluster
      """
      idx = 0; minDeltaR = 999
      def deltaR( eta1: float, phi1: float, eta2: float, phi2: float ) -> float:
        deta = abs( eta1 - eta2 )
        dphi = abs( phi1 - phi2 ) if abs(phi1 - phi2) < np.pi else (2*np.pi-abs(phi1-phi2))
        return np.sqrt( deta*deta + dphi*dphi )
      for trk in self:
        dR = deltaR( 0.0, 0.0, trk.trkClusDeta(), trk.trkClusDphi() )
        if dR < minDeltaR:
          minDeltaR = dR
          idx = self.getPos()
      self.setPos(idx)










