
__all__ = []

import numpy as np
import math

from loguru import logger
from typing import List, Any, Optional, Dict
from trig_egamma_frame import StatusCode
from trig_egamma_frame.emulator import Accept
from trig_egamma_frame import GeV



class PrecisionCalo:
    """
    PrecisionCalo hypo tool for precision calorimeter emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        AcceptAll (bool): If True, all clusters are accepted.
        ETthr (float): ET threshold value.
        dPHICLUSTERthr (float): Delta phi threshold between cluster and RoI.
        dETACLUSTERthr (float): Delta eta threshold between cluster and RoI.
    """

    def __init__(self, 
                 name: str, 
                 AcceptAll: bool = False,
                 ETthr: float = 0.0,
                 dPHICLUSTERthr: float = 0.0,
                 dETACLUSTERthr: float = 0.2):
        """
        Initialize the PrecisionCalo hypo tool.
        """
        self.name = name
        self.AcceptAll = AcceptAll
        self.ETthr = ETthr
        self.dPHICLUSTERthr = dPHICLUSTERthr
        self.dETACLUSTERthr = dETACLUSTERthr

    def initialize(self) -> StatusCode:
        """
        Initialize the PrecisionCalo hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the PrecisionCalo hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the PrecisionCalo hypo for a given context.
        
        Args:
            context: The execution context.
            
        Returns:
            Accept: The acceptance result.
        """
        clCont = context.getHandler("HLT__CaloClusterContainer")
        current = clCont.getPos()

        pClus = context.getHandler("HLT__TrigEMClusterContainer")
        emTauRoi = pClus.emTauRoI()
        
        phiRef = emTauRoi.phi()
        etaRef = emTauRoi.eta()

        if abs(etaRef) > 2.6:
            logger.debug( 'The cluster had eta coordinates beyond the EM fiducial volume.')
            return Accept(self.name, [("Pass", False)])
        
        if math.fabs(phiRef) > np.pi:
            phiRef -= 2 * np.pi

        bitAccept = [False for _ in range(clCont.size())]

        for cl in clCont:
            passed = False
            if self.AcceptAll:
                passed = True
            else:
                deta = abs(etaRef - cl.eta())
                dphi = abs(phiRef - cl.phi())
                if math.fabs(dphi) > np.pi:
                    dphi -= 2 * np.pi
                dphi = abs(dphi)

                if deta < self.dETACLUSTERthr:
                    if dphi < self.dPHICLUSTERthr:
                        if cl.et() > self.ETthr:
                            passed = True

            bitAccept[cl.getPos()] = passed

        clCont.setPos(current)
        passed = any(bitAccept)
        return Accept(self.name, [("Pass", passed)])


def configure(name: str, cpart: Dict[str, Any]) -> PrecisionCalo:
    """
    Configure the PrecisionCalo hypo tool.
    
    Args:
        name (str): The name of the hypo tool.
        cpart (dict): Chain configuration dictionary.
        
    Returns:
        PrecisionCalo: The configured PrecisionCalo hypo tool.
    """
    threshold = cpart['threshold']
    sel = 'ion' if 'ion' in cpart['extra'] else (cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo'])
    
    hypo = PrecisionCalo(name)
    hypo.ETthr = threshold * GeV
    hypo.dETACLUSTERthr = 0.1
    hypo.dPHICLUSTERthr = 0.1

    if sel in ('nocut', 'etcut', 'nopid', 'ion'):
        hypo.ETthr = threshold * GeV
        hypo.dETACLUSTERthr = 9999.
        hypo.dPHICLUSTERthr = 9999.

    return hypo

 

