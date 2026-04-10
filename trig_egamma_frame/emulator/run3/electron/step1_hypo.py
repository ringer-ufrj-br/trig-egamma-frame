

__all__ = []

import os
import numpy as np
import math

from loguru import logger
from typing import List, Any, Optional, Dict
from trig_egamma_frame import StatusCode
from trig_egamma_frame.emulator import Accept
from trig_egamma_frame.emulator.run3.selector import L2CaloCutMaps, RingerSelector
from trig_egamma_frame.emulator.run3.menu import electronFlags, treat_pidname
from trig_egamma_frame import GeV
from ROOT import TEnv



def same(value: Any) -> List[Any]:
    """
    Returns a list of 9 identical values.
    
    Args:
        value: The value to replicate.
        
    Returns:
        List[Any]: A list containing the value repeated 9 times.
    """
    return [value] * 9

class L2Calo:
    """
    L2Calo hypo tool for Layer 2 Calorimeter emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        AcceptAll (bool): If True, all clusters are accepted.
        UseRinger (bool): If True, use Ringer for selection.
        EtaBins (List[float]): List of eta bin boundaries.
        ETthr (List[float]): ET thresholds for each eta bin.
        dETACLUSTERthr (float): Delta eta threshold between cluster and RoI.
        dPHICLUSTERthr (float): Delta phi threshold between cluster and RoI.
        F1thr (List[float]): F1 thresholds for each eta bin.
        ET2thr (List[float]): High ET thresholds for each eta bin.
        HADET2thr (List[float]): Hadronic ET thresholds for high ET bin.
        HADETthr (List[float]): Hadronic ET thresholds for each eta bin.
        WETA2thr (List[float]): Weta2 thresholds for each eta bin.
        WSTOTthr (List[float]): Wstot thresholds for each eta bin.
        F3thr (List[float]): F3 thresholds for each eta bin.
        CARCOREthr (List[float]): Rcore thresholds for each eta bin.
        CAERATIOthr (List[float]): Eratio thresholds for each eta bin.
        ConfigPath (Optional[str]): Path to Ringer configuration file.
        EtCut (float): ET cut value for Ringer.
    """

    def __init__(self, 
                 name: str, 
                 AcceptAll: bool = False,
                 UseRinger: bool = False,
                 EtaBins: List[float] = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47],
                 ETthr: List[float] = same(0),
                 dETACLUSTERthr: float = 0.1,
                 dPHICLUSTERthr: float = 0.1,
                 F1thr: List[float] = same(0.005),
                 ET2thr: List[float] = same(90.0 * GeV),
                 HADET2thr: List[float] = same(999.0),
                 HADETthr: List[float] = same(999.0),
                 WETA2thr: List[float] = same(99999.),
                 WSTOTthr: List[float] = same(99999.),
                 F3thr: List[float] = same(99999.),
                 CARCOREthr: List[float] = same(999.0),
                 CAERATIOthr: List[float] = same(999.0),
                 ConfigPath: Optional[str] = None,
                 EtCut: float = -999.0):
        """
        Initialize the L2Calo hypo tool.
        """
        self.name = name
        self.AcceptAll = AcceptAll
        self.UseRinger = UseRinger
        self.EtaBins = EtaBins
        self.ETthr = ETthr
        self.dETACLUSTERthr = dETACLUSTERthr
        self.dPHICLUSTERthr = dPHICLUSTERthr
        self.F1thr = F1thr
        self.ET2thr = ET2thr
        self.HADET2thr = HADET2thr
        self.HADETthr = HADETthr
        self.WETA2thr = WETA2thr
        self.WSTOTthr = WSTOTthr
        self.F3thr = F3thr
        self.CARCOREthr = CARCOREthr
        self.CAERATIOthr = CAERATIOthr
        self.ConfigPath = ConfigPath
        self.EtCut = EtCut
        self.ringer = None

    def initialize(self) -> StatusCode:
        """
        Initialize the L2Calo hypo tool, loading Ringer if needed.
        
        Returns:
            StatusCode: SUCCESS or FAILURE.
        """
        if self.UseRinger:
            logger.info( f"Loading ringer models from {self.ConfigPath}")
            self.ringer = RingerSelector(ConfigPath=self.ConfigPath)
            if self.ringer.initialize().isFailure():
                logger.error( "Its not possible to initialize the ringer selector.")
                return StatusCode.FAILURE

        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the L2Calo hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the L2Calo hypo for a given context.
        
        Args:
            context: The execution context.
            
        Returns:
            Accept: The acceptance result.
        """
        if self.UseRinger:
            passed = self.emulate_ringer(context)
        else:
            passed = self.emulate(context)

        return Accept(self.name, [("Pass", passed)])

    def emulate(self, context: Any) -> bool:
        """
        Perform L2 calorimenter emulation.
        
        Args:
            context: The execution context.
            
        Returns:
            bool: True if context is accepted.
        """
        pClus = context.getHandler("HLT__TrigEMClusterContainer")
        emTauRoi = pClus.emTauRoI()
        PassedCuts = 0

        phiRef = emTauRoi.phi()
        etaRef = emTauRoi.eta()

        if abs(etaRef) > 2.6:
            logger.debug( 'The cluster had eta coordinates beyond the EM fiducial volume.')
            return False

        if self.AcceptAll:
            logger.debug( "Accept all.")
            return True

        if math.fabs(phiRef) > np.pi:
            phiRef -= 2 * np.pi

        absEta = math.fabs(pClus.eta())
        etaBin = -1
        if absEta > self.EtaBins[-1]:
            absEta = self.EtaBins[-1]
        
        for idx, value in enumerate(self.EtaBins[:-1]):
            if (absEta >= self.EtaBins[idx] and absEta < self.EtaBins[idx + 1]):
                etaBin = idx
                break

        inCrack = True if (absEta > 2.37 or (absEta > 1.37 and absEta < 1.52)) else False

        dPhi = math.fabs(pClus.phi() - phiRef)
        dPhi = dPhi if (dPhi < np.pi) else (2 * np.pi - dPhi)

        energyRatio = 0.0
        if (pClus.emaxs1() + pClus.e2tsts1()) > 0:
            energyRatio = (pClus.emaxs1() - pClus.e2tsts1()) / float(pClus.emaxs1() + pClus.e2tsts1())

        rCore = 0.0
        if (pClus.e277() != 0.0):
            rCore = pClus.e237() / float(pClus.e277())

        F1 = pClus.f1()
        eT_T2Calo = float(pClus.et())

        hadET_T2Calo = 0.0
        if (eT_T2Calo != 0 and pClus.eta() != 0):
            hadET_T2Calo = pClus.ehad1() / math.cosh(math.fabs(pClus.eta())) / eT_T2Calo

        Weta2 = pClus.weta2()
        Wstot = pClus.wstot()
        F3 = pClus.f3()

        if (math.fabs(pClus.eta() - etaRef) > self.dETACLUSTERthr):
            return False
        PassedCuts += 1

        if (dPhi > self.dPHICLUSTERthr):
            logger.debug( 'dphi > dphicluster')
            return False
        PassedCuts += 1

        if (etaBin == -1):
            logger.debug( "Cluster eta: %1.3f  outside eta range ", absEta)
            return False
        PassedCuts += 1

        if (rCore < self.CARCOREthr[etaBin]): return False
        PassedCuts += 1

        if (inCrack or F1 < self.F1thr[etaBin]):
            logger.debug( "TrigEMCluster: InCrack= %d F1=%1.3f", inCrack, F1)
        else:
            if (energyRatio < self.CAERATIOthr[etaBin]): return False
        PassedCuts += 1

        if (eT_T2Calo < self.ETthr[etaBin]): return False
        PassedCuts += 1

        hadET_cut = 0.0
        if (eT_T2Calo > self.ET2thr[etaBin]):
            hadET_cut = self.HADET2thr[etaBin]
        else:
            hadET_cut = self.HADETthr[etaBin]

        if (hadET_T2Calo > hadET_cut): return False
        PassedCuts += 1
        PassedCuts += 1

        if (Weta2 > self.WETA2thr[etaBin]): return False
        PassedCuts += 1

        if (Wstot >= self.WSTOTthr[etaBin]): return False
        PassedCuts += 1

        if (F3 > self.F3thr[etaBin]): return False
        PassedCuts += 1

        MSG_DEBUG(self, 'T2Calo emulation approved...')
        return True

    def emulate_ringer(self, context: Any) -> bool:
        """
        Perform Ringer emulation.
        
        Args:
            context: The execution context.
            
        Returns:
            bool: True if context is accepted by Ringer.
        """
        fc = context.getHandler("HLT__TrigEMClusterContainer")
        et = fc.et()

        if self.AcceptAll:
            logger.debug( "Accept all")
            return True

        if et < self.EtCut:
            return False

        return self.ringer.emulate(context)


class L2CaloConfiguration:
    """
    Helper class to configure L2Calo based on chain information.
    """
    __operation_points = ['tight', 'medium', 'loose', 'vloose', 
                          'lhtight', 'lhmedium', 'lhloose', 'lhvloose',
                          'dnntight', 'dnnmedium', 'dnnloose', 'dnnvloose']

    def __init__(self, name: str, cpart: Dict[str, Any]):
        """
        Initialize the configuration helper.
        """
        self.__cand = cpart['trigType']
        self.__threshold = cpart['threshold']
        self.__sel = 'ion' if 'ion' in cpart['extra'] else (cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo'])
        self.__gsfinfo = cpart['gsfInfo'] if cpart['trigType'] == 'e' and cpart['gsfInfo'] else ''
        self.__idperfinfo = cpart['idperfInfo'] if cpart['trigType'] == 'e' and cpart['idperfInfo'] else ''
        self.__noringerinfo = cpart['L2IDAlg']
        self.__ringerVersion = cpart['rVersion'] if 'rVersion' in cpart.keys() else None

        self.hypo = L2Calo(name)
        self.hypo.AcceptAll = False
        self.hypo.UseRinger = False
        self.hypo.EtaBins = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]
        self.hypo.ETthr = same(self.__threshold * GeV)
        self.hypo.dETACLUSTERthr = 0.1
        self.hypo.dPHICLUSTERthr = 0.1
        self.hypo.F1thr = same(0.005)
        self.hypo.ET2thr = same(90.0 * GeV)
        self.hypo.HADET2thr = same(999.0)
        self.hypo.HADETthr = same(0.058)
        self.hypo.WETA2thr = same(99999.)
        self.hypo.WSTOTthr = same(99999.)
        self.hypo.F3thr = same(99999.)
        self.hypo.CARCOREthr = same(-9999.)
        self.hypo.CAERATIOthr = same(-9999.)

        logger.info( f'Signature :{self.__cand}')
        logger.info( f'Threshold :{self.__threshold}')
        logger.info( f'Pidname   :{self.__sel}')
        logger.info( f'noringerinfo :{self.__noringerinfo}')

    def pidname(self) -> str:
        """Returns the PID name."""
        return self.__sel

    def etthr(self) -> float:
        """Returns the ET threshold."""
        return self.__threshold

    def isElectron(self) -> bool:
        """Returns True if the candidate is an electron."""
        return 'e' in self.__cand

    def isPhoton(self) -> bool:
        """Returns True if the candidate is a photon."""
        return 'g' in self.__cand

    def noringerinfo(self) -> str:
        """Returns noringer information."""
        return self.__noringerinfo

    def gsfinfo(self) -> str:
        """Returns GSF information."""
        return self.__gsfinfo

    def idperfinfo(self) -> str:
        """Returns idperf information."""
        return self.__idperfinfo

    def nocut(self) -> None:
        """Configure L2Calo for no cuts."""
        MSG_INFO(self, 'Configure nocut')
        self.hypo.AcceptAll = True
        self.hypo.UseRinger = False
        self.hypo.ETthr = same(self.etthr() * GeV)
        self.hypo.dETACLUSTERthr = 9999.
        self.hypo.dPHICLUSTERthr = 9999.
        self.hypo.F1thr = same(0.0)
        self.hypo.HADETthr = same(9999.)
        self.hypo.CARCOREthr = same(-9999.)
        self.hypo.CAERATIOthr = same(-9999.)

    def etcut(self) -> None:
        """Configure L2Calo for ET cut only."""
        logger.info( 'Configure etcut or nopid')
        self.hypo.UseRinger = False
        self.hypo.ETthr = same((self.etthr() - 3) * GeV)
        self.hypo.dETACLUSTERthr = 9999.
        self.hypo.dPHICLUSTERthr = 9999.
        self.hypo.F1thr = same(0.0)
        self.hypo.HADETthr = same(9999.)
        self.hypo.CARCOREthr = same(-9999.)
        self.hypo.CAERATIOthr = same(-9999.)

    def noringer(self) -> None:
        """Configure L2Calo for non-Ringer selection."""
        logger.info( 'Configure noringer')
        self.hypo.UseRinger = False
        self.hypo.ETthr = same((self.etthr() - 3) * GeV)
        self.hypo.HADETthr = L2CaloCutMaps(self.etthr()).MapsHADETthr[self.pidname()]
        self.hypo.CARCOREthr = L2CaloCutMaps(self.etthr()).MapsCARCOREthr[self.pidname()]
        self.hypo.CAERATIOthr = L2CaloCutMaps(self.etthr()).MapsCAERATIOthr[self.pidname()]

    def nominal(self) -> None:
        """Configure L2Calo for nominal Ringer selection."""
        logger.info( 'Configure ringer')
        self.hypo.UseRinger = True
        self.hypo.EtCut = (self.etthr() - 3.) * GeV
        if not self.pidname() in self.__operation_points:
            logger.error( f"Bad selection name: {self.pidname()}")

        opnames = {
            'tight': 'Tight',
            'medium': 'Medium',
            'loose': 'Loose',
            'vloose': 'VeryLoose',
        }

        path = os.path.join(
            electronFlags.ringerVersion[self.__ringerVersion],
            'ElectronRinger{op}TriggerConfig.conf'.format(op=opnames[treat_pidname(self.pidname())])
        )
        self.hypo.ConfigPath = path

    def compile(self) -> None:
        """Compile the configuration based on PID and chain info."""
        if self.pidname() in ('etcut', 'ion', 'nopid'):
            self.etcut()
        elif self.pidname() in self.__operation_points and 'noringer' in self.noringerinfo() and self.isElectron():
            self.noringer()
        elif self.pidname() in self.__operation_points and 'noringer' not in self.noringerinfo() and self.isElectron():
            self.nominal()
        elif self.pidname() in self.__operation_points and self.isPhoton() and 'ringer' != self.noringerinfo():
            self.etcut()
        elif self.pidname() in self.__operation_points and self.isPhoton() and 'ringer' == self.noringerinfo():
            self.nominal()
        elif self.etthr() == 0:
            self.nocut()

def configure(name: str, chainPart: Dict[str, Any]):
    """
    Configure the L2Calo hypo tool.
    
    Args:
        name (str): The name of the hypo tool.
        chainPart (dict): Chain configuration dictionary.
        
    Returns:
        The configured L2Calo hypo tool.
    """
    config = L2CaloConfiguration(name, chainPart)
    config.compile()
    return config.hypo

