
__all__ = ['TrigEgammaPrecisionElectronHypoTool']

from typing import List, Any, Optional, Dict
from trig_egamma_frame.emulator import StatusCode
from trig_egamma_frame.emulator import Accept
from trig_egamma_frame import GeV
from loguru import logger
import numpy as np
import math

class PrecisionElectron:
    """
    PrecisionElectron hypo tool for precision electron emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        RelPtConeCut (float): Relative pT cone isolation cut value.
        AcceptAll (bool): If True, all electrons are accepted.
        ETthr (float): ET threshold value.
        dPHICLUSTERthr (float): Delta phi threshold between cluster and RoI.
        dETACLUSTERthr (float): Delta eta threshold between cluster and RoI.
        PidName (str): Name of the selection (PID) to apply.
        d0Cut (float): d0 cut for LRT.
        DoNoPid (bool): If True, do not apply PID selection.
    """

    def __init__(self, 
                 name: str, 
                 RelPtConeCut: float = -1.0,
                 AcceptAll: bool = False,
                 ETthr: float = 0.0,
                 dPHICLUSTERthr: float = 0.0,
                 dETACLUSTERthr: float = 0.2,
                 PidName: str = "",
                 d0Cut: float = -1.0,
                 DoNoPid: bool = False):
        """
        Initialize the PrecisionElectron hypo tool.
        """
        Messenger.__init__(self)
        self.name = name
        self.RelPtConeCut = RelPtConeCut
        self.AcceptAll = AcceptAll
        self.ETthr = ETthr
        self.dPHICLUSTERthr = dPHICLUSTERthr
        self.dETACLUSTERthr = dETACLUSTERthr
        self.PidName = PidName
        self.d0Cut = d0Cut
        self.DoNoPid = DoNoPid

    def initialize(self) -> StatusCode:
        """
        Initialize the PrecisionElectron hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the PrecisionElectron hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the PrecisionElectron hypo for all electrons in the container.
        
        Args:
            context: The execution context.
            
        Returns:
            Accept: The acceptance result.
        """
        elCont = context.getHandler("HLT__ElectronContainer")
        pClus = context.getHandler("HLT__TrigEMClusterContainer")

        current = elCont.getPos()
        bitAccept = [False for _ in range(elCont.size())]
        emTauRoI = pClus.emTauRoI()

        for el in elCont:
            passed = self.emulate(el, emTauRoI)
            bitAccept[el.getPos()] = passed

        elCont.setPos(current)
        passed = any(bitAccept)
        return Accept(self.name, [("Pass", passed)])

    def emulate(self, el: Any, roi: Any) -> bool:
        """
        Perform precision electron emulation logic.
        
        Args:
            el: The electron object.
            roi: The RoI object for reference.
            
        Returns:
            bool: True if the electron passes all cuts.
        """
        phiRef = roi.phi()
        etaRef = roi.eta()

        if math.fabs(phiRef) > np.pi:
            phiRef -= 2 * np.pi

        if self.AcceptAll:
            return True

        if abs(etaRef) > 2.6:
            logger.debug( 'The cluster had eta coordinates beyond the EM fiducial volume.')
            return False

        cl = el.caloCluster()
        trk = el.trackParticle()

        deta = abs(etaRef - cl.eta())
        dphi = abs(phiRef - cl.phi())
        if math.fabs(dphi) > np.pi:
            dphi -= 2 * np.pi
        dphi = abs(dphi)

        if deta > self.dETACLUSTERthr:
            return False
        if dphi > self.dPHICLUSTERthr:
            return False
        if cl.et() < self.ETthr:
            return False

        if self.DoNoPid:
            return True

        if self.d0Cut > 0.0:
            d0 = trk.d0()
            if d0 < self.d0Cut:
                return False

        if not el.accept('trig_EF_el_' + self.PidName):
            return False

        ptvarcone20 = el.ptvarcone20()
        relptvarcone20 = ptvarcone20 / el.pt()

        if self.RelPtConeCut < -100:
            logger.debug( "not applying isolation. Returning NOW")
            return True

        if relptvarcone20 > self.RelPtConeCut:
            return False

        return True


class PrecisionElectronConfiguration:
    """
    Helper class to configure PrecisionElectron based on chain information.
    """
    __operation_points = ['tight', 'medium', 'loose', 'vloose', 
                          'lhtight', 'lhmedium', 'lhloose', 'lhvloose',
                          'dnntight', 'dnnmedium', 'dnnloose', 'mergedtight', 'nopid']

    __isolationCut = {
        None: None,
        'ivarloose': 0.1,
        'ivarmedium': 0.065,
        'ivartight': 0.05
    }

    __lrtD0Cut = {
        '': -1.,
        None: None,
        'lrtloose': 2.0,
        'lrtmedium': 3.0,
        'lrttight': 5.0
    }

    def __init__(self, name: str, cpart: Dict[str, Any]):
        """
        Initialize the PrecisionElectron configuration helper.
        """
        self.__threshold = cpart['threshold']
        self.__sel = cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo']
        self.__iso = cpart['isoInfo']
        self.__d0 = cpart['lrtInfo']
        self.__gsfInfo = cpart['gsfInfo']
        self.__lhInfo = cpart['lhInfo']

        self.hypo = PrecisionElectron(name)
        self.hypo.ETthr = self.__threshold * GeV
        self.hypo.dETACLUSTERthr = 0.1
        self.hypo.dPHICLUSTERthr = 0.1
        self.hypo.RelPtConeCut = -999
        self.hypo.PidName = ""
        self.hypo.d0Cut = -1
        self.hypo.AcceptAll = False
        self.hypo.DoNoPid = False

        logger.info( f'Electron_Threshold :{self.__threshold}')
        logger.info( f'Electron_Pidname   :{self.pidname()}')
        logger.info( f'Electron_iso       :{self.__iso}')
        logger.info( f'Electron_d0        :{self.__d0}')

    def pidname(self) -> str:
        """Returns the PID name."""
        return self.__sel

    def etthr(self) -> float:
        """Returns the ET threshold."""
        return self.__threshold

    def isoInfo(self) -> str:
        """Returns isolation information."""
        return self.__iso

    def d0Info(self) -> str:
        """Returns d0 information."""
        return self.__d0

    def gsfInfo(self) -> str:
        """Returns GSF information."""
        return self.__gsfInfo

    def nocut(self) -> None:
        """Configure PrecisionElectron for no cuts."""
        logger.info( 'Configure nocut')
        self.hypo.ETthr = self.etthr() * GeV
        self.hypo.dETACLUSTERthr = 9999.
        self.hypo.dPHICLUSTERthr = 9999.

    def noPid(self) -> None:
        """Configure PrecisionElectron for no PID selection."""
        logger.info( 'Configure noPid')
        self.hypo.DoNoPid = True
        self.hypo.ETthr = self.etthr() * GeV
        self.hypo.dETACLUSTERthr = 9999.
        self.hypo.dPHICLUSTERthr = 9999.

    def addLRTCut(self) -> None:
        """Add LRT cuts if applicable."""
        if self.d0Info() not in self.__lrtD0Cut:
            logger.error( f"Bad LRT selection name: {self.d0Info()}")
        self.hypo.d0Cut = self.__lrtD0Cut[self.d0Info()]

    def acceptAll(self) -> None:
        """Accept all electrons."""
        self.hypo.AcceptAll = True

    def addIsoCut(self) -> None:
        """Add isolation cuts if applicable."""
        if self.isoInfo() not in self.__isolationCut:
            logger.error( f"Bad Iso selection name: {self.isoInfo()}")
        self.hypo.RelPtConeCut = self.__isolationCut[self.isoInfo()]

    def nominal(self) -> None:
        """Configure PrecisionElectron for nominal selection."""
        if self.pidname() not in self.__operation_points:
            logger.error( "Bad selection name: %s" % self.pidname())
        self.hypo.PidName = self.pidname()

    def compile(self) -> None:
        """Compile the configuration based on PID and chain info."""
        if 'nocut' == self.pidname():
            self.nocut()
        elif 'nopid' == self.pidname():
            self.noPid()
        else:
            self.nominal()

        if self.isoInfo() and self.isoInfo() != "":
            logger.info( "Adding IsoCut...")
            self.addIsoCut()
        
        if self.d0Info() and self.d0Info() != "":
            logger.info( "Adding LRTCut...")
            self.addLRTCut()


def configure(name: str, chainPart: Dict[str, Any]) -> PrecisionElectron:
    """
    Configure the PrecisionElectron hypo tool.
    
    Args:
        name (str): The name of the hypo tool.
        chainPart (dict): Chain configuration dictionary.
        
    Returns:
        PrecisionElectron: The configured PrecisionElectron hypo tool.
    """
    config = PrecisionElectronConfiguration(name, chainPart)
    config.compile()
    return config.hypo

