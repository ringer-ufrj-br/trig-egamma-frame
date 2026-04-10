
__all__ = []

import math
import re

from loguru import logger
from typing import List, Any, Optional, Dict
from trig_egamma_frame import StatusCode
from trig_egamma_frame.emulator import Accept


class L1Calo:
    """
    L1Calo hypo tool for legacy L1 emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        WPNames (List[str]): List of Working Point names.
        HadCoreCutMin (List[float]): Minimum Hadronic core cut values.
        HadCoreCutOff (List[float]): Hadronic core cut offset values.
        HadCoreSlope (List[float]): Hadronic core cut slope values.
        EmIsolCutMin (List[float]): Minimum EM isolation cut values.
        EmIsolCutOff (List[float]): EM isolation cut offset values.
        EmIsolSlope (List[float]): EM isolation cut slope values.
        IsolCutMax (float): Maximum isolation cut value.
        L1Item (str): Name of the L1 item (e.g., 'L1_EM3').
    """

    def __init__(self, 
                 name: str, 
                 WPNames: List[str] = ['Tight', 'Medium', 'Loose'],
                 HadCoreCutMin: List[float] = [1.0, 1.0, 1.0, 1.0],
                 HadCoreCutOff: List[float] = [-0.2, -0.2, -0.2, -0.2],
                 HadCoreSlope: List[float] = [1/23., 1/23., 1/23., 1/23.],
                 EmIsolCutMin: List[float] = [2.0, 1.0, 1.0, 1.5],
                 EmIsolCutOff: List[float] = [-1.8, -2.6, -2.0, -1.8],
                 EmIsolSlope: List[float] = [1/8., 1/8., 1/8., 1/8.],
                 IsolCutMax: float = 50.0,
                 L1Item: str = 'L1_EM3'):
        """
        Initialize the L1Calo hypo tool with specified or default parameters.
        """
        self.name = name
        self.WPNames = WPNames
        self.HadCoreCutMin = HadCoreCutMin
        self.HadCoreCutOff = HadCoreCutOff
        self.HadCoreSlope = HadCoreSlope
        self.EmIsolCutMin = EmIsolCutMin
        self.EmIsolCutOff = EmIsolCutOff
        self.EmIsolSlope = EmIsolSlope
        self.IsolCutMax = IsolCutMax
        self.L1Item = L1Item

    def initialize(self) -> StatusCode:
        """
        Initialize the L1Calo hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the L1Calo hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the L1Calo hypo for a given context.
        
        Args:
            context: The execution context containing event data.
            
        Returns:
            Accept: The acceptance result.
        """
        l1 = context.getHandler("HLT__EmTauRoIContainer")
        passed = self.emulate(l1, self.L1Item)
        return Accept(self.name, [("Pass", passed)])

    def emulate(self, l1: Any, L1Item: str) -> bool:
        """
        Perform L1 legacy emulation.
        
        Args:
            l1: The L1 RoI object.
            L1Item (str): The L1 item name.
            
        Returns:
            bool: True if the RoI passes the emulation.
        """
        l1type      = self.L1Item.replace('L1_EM','') # L1_EM3 to EM3
        l1threshold = float(re.findall('\d+', l1type)[0])

        c = 0
        if (self.WPNames[0] in l1type): c = 1  # Tight
        if (self.WPNames[1] in l1type): c = 2  # Medium
        if (self.WPNames[2] in l1type): c = 3  # Loose

        hadCoreCutMin = self.HadCoreCutMin[c]
        hadCoreCutOff = self.HadCoreCutOff[c]
        hadCoreSlope = self.HadCoreSlope[c]
        emIsolCutMin = self.EmIsolCutMin[c]
        emIsolCutOff = self.EmIsolCutOff[c]
        emIsolCutSlope = self.EmIsolSlope[c]

        emE = l1.emClus() / 1.e3   # Cluster energy
        eta = l1.eta()             # eta
        hadCore = l1.hadCore() / 1.e3  # Hadronic core energy
        emIsol = l1.emIsol() / 1.e3    # EM Isolation energy

        if ('H' in l1type):
            logger.debug( "L1 (H) CUT")
            if not self.isolationL1(hadCoreCutMin, hadCoreCutOff, hadCoreSlope, hadCore, emE):
                logger.debug( "rejected")
                return False
            logger.debug( "accepted")

        if ('I' in l1type):
            logger.debug( "L1 (I) CUT")
            if not self.isolationL1(emIsolCutMin, emIsolCutOff, emIsolCutSlope, emIsol, emE):
                logger.debug( "rejected")
                return False
            logger.debug( "accepted")

        if ('V' in l1type):
            logger.debug( "L1 (V) CUT")
            if not self.variableEtL1(l1type, emE, eta):
                logger.debug( "rejected")
                return False
            logger.debug( "accepted")

        if (emE <= l1threshold):
            return False

        return True

    def isolationL1(self, min_: float, offset: float, slope: float, energy: float, emE: float) -> bool:
        """
        Evaluate L1 hadronic core or EM isolation cut.
        
        Args:
            min_ (float): Minimum isolation value.
            offset (float): Isolation offset.
            slope (float): Isolation slope.
            energy (float): The energy to be tested (hadronic or EM isolation).
            emE (float): The total EM cluster energy.
            
        Returns:
            bool: True if it passes the isolation cut.
        """
        if (emE > self.IsolCutMax):
            logger.debug( "L1 Isolation skipped, ET > Maximum isolation")
            return True

        isolation = offset + emE * slope
        if (isolation < min_): isolation = min_

        value = False if (energy > isolation) else True
        return value

    def variableEtL1(self, L1item: str, l1energy: float, l1eta: float) -> bool:
        """
        Evaluate variable Et cut for L1.
        
        Args:
            L1item (str): The L1 item name.
            l1energy (float): The L1 cluster energy.
            l1eta (float): The L1 cluster eta.
            
        Returns:
            bool: True if passes the variable Et cut.
        """
        cut = self.emulationL1V(L1item, l1eta)
        energy = l1energy
        value = False if (energy <= cut) else True
        return value

    def emulationL1V(self, L1item: str, l1eta: float) -> float:
        """
        Perform eta-dependent L1 variable Et cut calculation.
        
        Args:
            L1item (str): The L1 item name.
            l1eta (float): The L1 cluster eta.
            
        Returns:
            float: The calculated cut value.
        """
        cut = 0.0
        eta = math.fabs(l1eta)

        if (L1item == "50V"):
            if (eta >= 0.8 and eta < 1.2): cut = 51.0
            elif (eta >= 1.2 and eta < 1.6): cut = 50.0
            elif (eta >= 1.6 and eta < 2.0): cut = 51.0
            else: cut = 52
        elif (L1item == "8VH"):
            if   (eta > 0.8 and eta <= 1.1): cut = 7.0
            elif (eta > 1.1 and eta <= 1.4): cut = 6.0
            elif (eta > 1.4 and eta <= 1.5): cut = 5.0
            elif (eta > 1.5 and eta <= 1.8): cut = 7.0
            elif (eta > 1.8 and eta <= 2.5): cut = 8.0
            else: cut = 9.0
        elif (L1item == "10VH"):
            if   (eta > 0.8 and eta <= 1.1): cut = 9.0
            elif (eta > 1.1 and eta <= 1.4): cut = 8.0
            elif (eta > 1.4 and eta <= 1.5): cut = 7.0
            elif (eta > 1.5 and eta <= 1.8): cut = 9.0
            elif (eta > 1.8 and eta <= 2.5): cut = 10.0
            else: cut = 11.0
        elif (L1item == "13VH"):
            if   (eta > 0.7 and eta <= 0.9): cut = 14.0
            elif (eta > 0.9 and eta <= 1.2): cut = 13.0
            elif (eta > 1.2 and eta <= 1.4): cut = 12.0
            elif (eta > 1.4 and eta <= 1.5): cut = 11.0
            elif (eta > 1.5 and eta <= 1.7): cut = 13.0
            elif (eta > 1.7 and eta <= 2.5): cut = 14.0
            else: cut = 15.0
        elif (L1item == "15VH"):
            if   (eta > 0.7 and eta <= 0.9): cut = 16.0
            elif (eta > 0.9 and eta <= 1.2): cut = 15.0
            elif (eta > 1.2 and eta <= 1.4): cut = 14.0
            elif (eta > 1.4 and eta <= 1.5): cut = 13.0
            elif (eta > 1.5 and eta <= 1.7): cut = 15.0
            elif (eta > 1.7 and eta <= 2.5): cut = 16.0
            else: cut = 17.0
        elif (L1item == "18VH"):
            if   (eta > 0.7 and eta <= 0.8): cut = 19.0
            elif (eta > 0.8 and eta <= 1.1): cut = 18.0
            elif (eta > 1.1 and eta <= 1.3): cut = 17.0
            elif (eta > 1.3 and eta <= 1.4): cut = 16.0
            elif (eta > 1.4 and eta <= 1.5): cut = 15.0
            elif (eta > 1.5 and eta <= 1.7): cut = 17.0
            elif (eta > 1.7 and eta <= 2.5): cut = 19.0
            else: cut = 20.0
        elif (L1item == "20VH"):
            if   (eta > 0.7 and eta <= 0.8): cut = 21.0
            elif (eta > 0.8 and eta <= 1.1): cut = 20.0
            elif (eta > 1.1 and eta <= 1.3): cut = 19.0
            elif (eta > 1.3 and eta <= 1.4): cut = 18.0
            elif (eta > 1.4 and eta <= 1.5): cut = 17.0
            elif (eta > 1.5 and eta <= 1.7): cut = 19.0
            elif (eta > 1.7 and eta <= 2.5): cut = 21.0
            else: cut = 22.0
        elif (L1item == "20VHI"):
            if   (eta > 0.7 and eta <= 0.8): cut = 21.0
            elif (eta > 0.8 and eta <= 1.1): cut = 20.0
            elif (eta > 1.1 and eta <= 1.3): cut = 19.0
            elif (eta > 1.3 and eta <= 1.4): cut = 18.0
            elif (eta > 1.4 and eta <= 1.5): cut = 17.0
            elif (eta > 1.5 and eta <= 1.7): cut = 19.0
            elif (eta > 1.7 and eta <= 2.5): cut = 21.0
            else: cut = 22.0
        elif (L1item == "22VHI"):
            if   (eta > 0.7 and eta <= 0.8): cut = 23.0
            elif (eta > 0.8 and eta <= 1.1): cut = 22.0
            elif (eta > 1.1 and eta <= 1.3): cut = 21.0
            elif (eta > 1.3 and eta <= 1.4): cut = 20.0
            elif (eta > 1.4 and eta <= 1.5): cut = 19.0
            elif (eta > 1.5 and eta <= 1.7): cut = 21.0
            elif (eta > 1.7 and eta <= 2.5): cut = 23.0
            else: cut = 24.0

        return cut


class L1Calo_eFEX:
    """
    L1Calo hypo tool for eFEX L1 emulation.
    
    Attributes:
        name (str): The name of the hypo tool.
        L1Item (str): Name of the L1 item (e.g., 'L1_EM3').
    """
    def __init__(self, name: str, L1Item: str = 'L1_EM3'):
        """
        Initialize the L1Calo_eFEX hypo tool.
        """
        self.name = name
        self.L1Item = L1Item

    def initialize(self) -> StatusCode:
        """
        Initialize the L1Calo_eFEX hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def finalize(self) -> StatusCode:
        """
        Finalize the L1Calo_eFEX hypo tool.
        
        Returns:
            StatusCode: SUCCESS.
        """
        return StatusCode.SUCCESS

    def accept(self, context: Any) -> Accept:
        """
        Evaluate the L1Calo_eFEX hypo for a given context.
        
        Args:
            context: The execution context.
            
        Returns:
            Accept: The acceptance result.
        """
        return Accept(self.name, [("Pass", True)])


def configure(name: str, chainPart: Dict[str, Any]):
    """
    Configure the L1 hypo tool using the trigger chain information.
    
    Args:
        name (str): The name of the hypo tool.
        chainPart (dict): The dictionary containing chain configuration.
        
    Returns:
        Messenger: The configured hypo tool (L1Calo or L1Calo_eFEX).
    """
    from trig_egamma_frame.emulator import electronFlags
    l1item = chainPart['L1Threshold']

    if electronFlags.L1Legacy:
        hypo = L1Calo(name,
                      WPNames=['Tight', 'Medium', 'Loose'],
                      HadCoreCutMin=[1.0, 1.0, 1.0, 1.0],
                      HadCoreCutOff=[-0.2, -0.2, -0.2, -0.2],
                      HadCoreSlope=[1/23., 1/23., 1/23., 1/23.],
                      EmIsolCutMin=[2.0, 1.0, 1.0, 1.5],
                      EmIsolCutOff=[-1.8, -2.6, -2.0, -1.8],
                      EmIsolSlope=[1/8., 1/8., 1/8., 1/8.],
                      IsolCutMax=50.0,
                      L1Item=l1item)
    else:
        hypo = L1Calo_eFEX(name, L1Item=l1item)
    return hypo

