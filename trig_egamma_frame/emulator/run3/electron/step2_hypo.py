
__all__ = ['L2Electron']

from typing import List, Any, Optional, Dict
from egamma.core import Messenger, StatusCode
from egamma.core.macros import *
from egamma.emulator import Accept
from egamma import GeV

import numpy as np
import math

class L2Electron(Messenger):
    """
    L2Electron hypo tool for Layer 2 electron emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        EtCut (float): ET cut value.
        TrackPt (float): Track PT cut value.
        CaloTrackdETA (float): Delta eta cut between cluster and track.
        CaloTrackdPHI (float): Delta phi cut between cluster and track.
        CaloTrackdEoverPLow (float): Lower bound for E/p ratio cut.
        CaloTrackdEoverPHigh (float): Upper bound for E/p ratio cut.
        TRTRatio (float): TRT hit ratio cut.
        d0Cut (float): d0 cut for LRT.
        DoLRT (bool): If True, apply Large Radius Tracking cuts.
        AcceptAll (bool): If True, accept all electrons.
    """

    def __init__(self, 
                 name: str, 
                 EtCut: float = 0.0,
                 TrackPt: float = 0.0,
                 CaloTrackdETA: float = 0.2,
                 CaloTrackdPHI: float = 0.3,
                 CaloTrackdEoverPLow: float = 0.0,
                 CaloTrackdEoverPHigh: float = 999.0,
                 TRTRatio: float = -999.0,
                 d0Cut: float = -999.0,
                 DoLRT: bool = False):
        """
        Initialize the L2Electron hypo tool.
        """
        Messenger.__init__(self, name)
        self.name = name
        self.EtCut = EtCut
        self.TrackPt = TrackPt
        self.CaloTrackdETA = CaloTrackdETA
        self.CaloTrackdPHI = CaloTrackdPHI
        self.CaloTrackdEoverPLow = CaloTrackdEoverPLow
        self.CaloTrackdEoverPHigh = CaloTrackdEoverPHigh
        self.TRTRatio = TRTRatio
        self.d0Cut = d0Cut
        self.DoLRT = DoLRT
        self.AcceptAll = False

    def initialize(self) -> StatusCode:
        """
        Initialize the L2Electron hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the L2Electron hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the L2Electron hypo for all electrons in the container.
        
        Args:
            context: The execution context.
            
        Returns:
            Accept: The acceptance result.
        """
        elCont = context.getHandler("HLT__TrigElectronContainer")
        current = elCont.getPos()
        bitAccept = [False for _ in range(elCont.size())]

        for el in elCont:
            dPhiCalo = el.trkClusDphi()
            dEtaCalo = el.trkClusDeta()
            pTcalo = el.pt()
            eTOverPt = el.etOverPt()
            NTRHits = el.numberOfTRTHits()
            NStrawHits = el.numberOfTRTHiThresholdHits()
            TRTHitRatio = 1e10 if NStrawHits == 0 else NTRHits / float(NStrawHits)
            d0 = el.d0()

            passed = False
            if self.AcceptAll:
                passed = True
            elif (pTcalo > self.TrackPt):
                if (dEtaCalo < self.CaloTrackdETA):
                    if (dPhiCalo < self.CaloTrackdPHI):
                        if (eTOverPt > self.CaloTrackdEoverPLow):
                            if (eTOverPt < self.CaloTrackdEoverPHigh):
                                if (TRTHitRatio > self.TRTRatio):
                                    if self.DoLRT and d0 > self.d0Cut:
                                        passed = True
                                        MSG_DEBUG(self, "Event LRT accepted !")
                                    elif not self.DoLRT:
                                        passed = True
                                        MSG_DEBUG(self, "Event accepted !")

            bitAccept[el.getPos()] = passed

        elCont.setPos(current)
        passed = any(bitAccept)
        return Accept(self.name, [("Pass", passed)])


class L2ElectronConfiguration(Messenger):
    """
    Helper class to configure L2Electron based on chain information.
    """
    __operation_points = ['tight', 'medium', 'loose', 'vloose', 
                          'lhtight', 'lhmedium', 'lhloose', 'lhvloose',
                          'mergedtight', 'dnntight', 'dnnmedium', 'dnnloose', 'dnnvloose']

    __trigElectronLrtd0Cut = {
        'lrtloose': 2.0,
        'lrtmedium': 3.0,
        'lrttight': 5.0
    }

    def __init__(self, name: str, cpart: Dict[str, Any]):
        """
        Initialize the L2Electron configuration helper.
        """
        Messenger.__init__(self)
        self.__threshold = cpart['threshold']
        self.__sel = cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo']
        self.__idperfInfo = cpart['idperfInfo']
        self.__lrtInfo = cpart['lrtInfo']
        self.hypo = L2Electron(name)
        
        MSG_INFO(self, 'Threshold :%s', self.__threshold)
        MSG_INFO(self, 'Pidname   :%s', self.__sel)

    def etthr(self) -> float:
        """Returns the ET threshold."""
        return self.__threshold

    def lrtInfo(self) -> str:
        """Returns LRT information."""
        return self.__lrtInfo

    def idperfInfo(self) -> str:
        """Returns idperf information."""
        return self.__idperfInfo

    def nocut(self) -> None:
        """Configure L2Electron for no cuts."""
        self.hypo.AcceptAll = True

    def nominal(self) -> None:
        """Configure L2Electron for nominal selection."""
        if self.etthr() < 15:
            self.hypo.TrackPt = 1.0 * GeV
        elif self.etthr() >= 15 and self.etthr() < 20:
            self.hypo.TrackPt = 2.0 * GeV
        elif self.etthr() >= 20 and self.etthr() < 50:
            self.hypo.TrackPt = 3.0 * GeV
        elif self.etthr() >= 50:
            self.hypo.TrackPt = 5.0 * GeV
            self.hypo.CaloTrackdETA = 999.
            self.hypo.CaloTrackdPHI = 999.

    def addLRTCut(self) -> None:
        """Add LRT cuts if applicable."""
        self.hypo.DoLRT = True
        self.hypo.d0Cut = self.__trigElectronLrtd0Cut[self.lrtInfo()]

    def compile(self) -> None:
        """Compile the configuration based on PID and chain info."""
        if 'idperf' in self.idperfInfo():
            MSG_INFO(self, "Configure nocut...")
            self.nocut()
        else:
            MSG_INFO(self, "Configure nominal...")
            self.nominal()
        
        if self.lrtInfo() in self.__trigElectronLrtd0Cut:
            MSG_INFO(self, "Adding LRT cuts...")
            self.addLRTCut()


def configure(name: str, chainPart: Dict[str, Any]) -> L2Electron:
    """
    Configure the L2Electron hypo tool.
    
    Args:
        name (str): The name of the hypo tool.
        chainPart (dict): Chain configuration dictionary.
        
    Returns:
        L2Electron: The configured L2Electron hypo tool.
    """
    config = L2ElectronConfiguration(name, chainPart)
    config.compile()
    return config.hypo
