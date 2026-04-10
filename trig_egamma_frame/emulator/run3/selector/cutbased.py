__all__ = ['CutBased', 'L2CaloCutMaps', 'L2CaloPhotonCutMaps']

import math
from typing import List, Optional, Any
import numpy as np
from loguru import logger

from trig_egamma_frame.kernel import StatusCode
from trig_egamma_frame.emulator.run3.electron import L2CaloCutMaps
from trig_egamma_frame import GeV


def same(value: Any) -> List[Any]:
    """
    Returns a list of 9 identical values.
    
    Args:
        value: The value to replicate.
        
    Returns:
        List[Any]: A list containing the value repeated 9 times.
    """
    return [value] * 9


class CutBased:
    """
    Cut-based selector for L2 Calorimeter emulation.
    
    This class implements the standard cut-based selection for L2 Calo clusters.
    
    Attributes:
        EtaBins (List[float]): List of eta bin boundaries.
        ETthr (List[float]): Transverse energy thresholds for each eta bin.
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
        ConfigPath (Optional[str]): Path to configuration file.
        EtCut (float): ET cut value.
    """

    def __init__(
        self,
        EtaBins: List[float] = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47],
        ETthr: Optional[List[float]] = None,
        dETACLUSTERthr: float = 0.1,
        dPHICLUSTERthr: float = 0.1,
        F1thr: Optional[List[float]] = None,
        ET2thr: Optional[List[float]] = None,
        HADET2thr: Optional[List[float]] = None,
        HADETthr: Optional[List[float]] = None,
        WETA2thr: Optional[List[float]] = None,
        WSTOTthr: Optional[List[float]] = None,
        F3thr: Optional[List[float]] = None,
        CARCOREthr: Optional[List[float]] = None,
        CAERATIOthr: Optional[List[float]] = None,
        ConfigPath: Optional[str] = None,
        EtCut: float = -999.0,
        **kw
    ):
        """
        Initialize the CutBased selector with properties.

        Args:
            EtaBins (List[float]): List of eta bin boundaries.
            ETthr (Optional[List[float]]): Transverse energy thresholds for each eta bin.
            dETACLUSTERthr (float): Delta eta cluster threshold.
            dPHICLUSTERthr (float): Delta phi cluster threshold.
            F1thr (Optional[List[float]]): F1 sampling fraction thresholds.
            ET2thr (Optional[List[float]]): ET thresholds for high energy cuts.
            HADET2thr (Optional[List[float]]): Hadronic ET thresholds for high energy.
            HADETthr (Optional[List[float]]): Hadronic ET thresholds.
            WETA2thr (Optional[List[float]]): Weta2 thresholds.
            WSTOTthr (Optional[List[float]]): Wstot thresholds.
            F3thr (Optional[List[float]]): F3 sampling fraction thresholds.
            CARCOREthr (Optional[List[float]]): Rcore thresholds.
            CAERATIOthr (Optional[List[float]]): Energy ratio thresholds.
            ConfigPath (Optional[str]): Path to the configuration file.
            EtCut (float): ET cut value.
            **kw: Additional keyword arguments.
        """
        self.EtaBins = EtaBins
        self.ETthr = ETthr if ETthr is not None else same(0)
        self.dETACLUSTERthr = dETACLUSTERthr
        self.dPHICLUSTERthr = dPHICLUSTERthr
        self.F1thr = F1thr if F1thr is not None else same(0.005)
        self.ET2thr = ET2thr if ET2thr is not None else same(90.0 * GeV)
        self.HADET2thr = HADET2thr if HADET2thr is not None else same(999.0)
        self.HADETthr = HADETthr if HADETthr is not None else same(999.0)
        self.WETA2thr = WETA2thr if WETA2thr is not None else same(99999.0)
        self.WSTOTthr = WSTOTthr if WSTOTthr is not None else same(99999.0)
        self.F3thr = F3thr if F3thr is not None else same(99999.0)
        self.CARCOREthr = CARCOREthr if CARCOREthr is not None else same(999.0)
        self.CAERATIOthr = CAERATIOthr if CAERATIOthr is not None else same(999.0)
        self.ConfigPath = ConfigPath
        self.EtCut = EtCut

    def initialize(self) -> StatusCode:
        """
        Initialize the selector.

        Returns:
            StatusCode: SUCCESS status.
        """
        return StatusCode.SUCCESS

    def emulate(self, context: Any, pidname: str) -> bool:
        """
        Perform emulation for a given context and PID name.

        Args:
            context (Any): The emulation context.
            pidname (str): The name of the PID to emulate.

        Returns:
            bool: True if emulation passes, False otherwise.
        """
        cl = context.getHandler("HLT__TrigEMClusterContainer")
        cuts = L2CaloCutMaps(cl.et() / GeV)

        self.HADETthr = cuts.MapsHADETthr[pidname]
        self.CARCOREthr = cuts.MapsCARCOREthr[pidname]
        self.CAERATIOthr = cuts.MapsCAERATIOthr[pidname]
        passed = self.accept(context)
        return passed

    def accept(self, context: Any) -> bool:
        """
        Apply selection cuts to the cluster in the context.

        Args:
            context (Any): The emulation context.

        Returns:
            bool: True if the cluster passes all cuts, False otherwise.
        """

        pClus = context.getHandler("HLT__TrigEMClusterContainer")
        # get the equivalent L1 EmTauRoi object in athena
        emTauRoi = pClus.emTauRoI()
        PassedCuts = 0

        # fill local variables for RoI reference position
        phiRef = emTauRoi.phi()
        etaRef = emTauRoi.eta()

        if abs(etaRef) > 2.6:
            logger.debug('The cluster had eta coordinates beyond the EM fiducial volume.')
            return False

        # correct phi the to right range (probably not needed anymore)
        if math.fabs(phiRef) > np.pi:
            phiRef -= 2 * np.pi  # correct phi if outside range

        absEta = math.fabs(pClus.eta())
        etaBin = -1
        if absEta > self.EtaBins[-1]:
            absEta = self.EtaBins[-1]
        # get the corrct eta bin range
        for idx, value in enumerate(self.EtaBins[:-1]):
            if absEta >= self.EtaBins[idx] and absEta < self.EtaBins[idx + 1]:
                etaBin = idx
                break

        # Is in crack region?
        inCrack = True if (absEta > 2.37 or (absEta > 1.37 and absEta < 1.52)) else False

        # Deal with angle diferences greater than Pi
        dPhi = math.fabs(pClus.phi() - phiRef)
        dPhi = dPhi if (dPhi < np.pi) else (2 * np.pi - dPhi)

        # calculate cluster quantities // definition taken from TrigElectron constructor
        energyRatio = 0.0
        if (pClus.emaxs1() + pClus.e2tsts1()) > 0:
            energyRatio = (pClus.emaxs1() - pClus.e2tsts1()) / float(pClus.emaxs1() + pClus.e2tsts1())

        # (VD) here the definition is a bit different to account for the cut of e277 @ EF
        rCore = 0.0
        if (pClus.e277() != 0.):
            rCore = pClus.e237() / float(pClus.e277())

        # fraction of energy deposited in 1st sampling
        F1 = pClus.f1()

        eT_T2Calo = float(pClus.et())

        hadET_T2Calo = 0.0
        if (eT_T2Calo != 0 and pClus.eta() != 0):
            hadET_T2Calo = pClus.ehad1() / math.cosh(math.fabs(pClus.eta())) / eT_T2Calo

        # extract Weta2 varable
        Weta2 = pClus.weta2()
        # extract Wstot varable
        Wstot = pClus.wstot()

        # extract F3 (backenergy i EM calorimeter
        F3 = pClus.f3()
        # apply cuts: DeltaEta(clus-ROI)
        if (math.fabs(pClus.eta() - etaRef) > self.dETACLUSTERthr):
            return False

        PassedCuts += 1  # Deta

        # DeltaPhi(clus-ROI)
        if (dPhi > self.dPHICLUSTERthr):
            logger.debug('dphi > dphicluster')
            return False

        PassedCuts += 1  # DPhi

        # eta range
        if (etaBin == -1):  # VD
            logger.debug("Cluster eta: %1.3f outside eta range ", absEta)
            return False
        else:
            logger.debug("eta bin used for cuts ")

        PassedCuts += 1  # passed eta cut

        # Rcore
        if (rCore < self.CARCOREthr[etaBin]):
            return False
        PassedCuts += 1  # Rcore

        # Eratio
        if (inCrack or F1 < self.F1thr[etaBin]):
            logger.debug("TrigEMCluster: InCrack= %d F1=%1.3f", inCrack, F1)
        else:
            if (energyRatio < self.CAERATIOthr[etaBin]):
                return False

        PassedCuts += 1  # Eratio
        if inCrack:
            energyRatio = -1  # Set default value in crack for monitoring.

        # ET_em
        if (eT_T2Calo * 1e-3 < self.ETthr[etaBin]):
            return False
        PassedCuts += 1  # ET_em

        hadET_cut = 0.0
        # find which ET_had to apply : this depends on the ET_em and the eta bin
        if (eT_T2Calo > self.ET2thr[etaBin]):
            hadET_cut = self.HADET2thr[etaBin]
        else:
            hadET_cut = self.HADETthr[etaBin]

        # ET_had
        if (hadET_T2Calo > hadET_cut):
            return False
        PassedCuts += 1  # ET_had
        # F1
        PassedCuts += 1  # F1
        # Weta2
        if (Weta2 > self.WETA2thr[etaBin]):
            return False
        PassedCuts += 1  # Weta2
        # Wstot
        if (Wstot >= self.WSTOTthr[etaBin]):
            return False
        PassedCuts += 1  # Wstot
        # F3
        if (F3 > self.F3thr[etaBin]):
            return False
        PassedCuts += 1  # F3
        # got this far => passed!
        logger.debug('T2Calo emulation approved...')
        return True

    def finalize(self) -> StatusCode:
        """
        Finalize the selector.

        Returns:
            StatusCode: SUCCESS status.
        """
        return StatusCode.SUCCESS


# Copyright (C) 2002-2017 CERN for the benefit of the ATLAS collaboration

# L2 Calo cut definitions for Electrons
# Ryan Mackenzie White <ryan.white@cern.ch>
# Akshay Katre
# Cuts migrated from L2CaloHypoConfig

class L2CaloCutMaps:
    """
    Cut maps for L2 Calorimeter electron hypo.
    
    This class defines the HADET, CAERATIO, and CARCORE threshold maps
    grouped by Et threshold and selection level.
    
    Attributes:
        MapsHADETthr (dict): Map of HADET threshold lists per selection level.
        MapsCAERATIOthr (dict): Map of CAERATIO threshold lists per selection level.
        MapsCARCOREthr (dict): Map of CARCORE threshold lists per selection level.
    """
    def __init__(self, threshold: float) -> None:
        """
        Initialize cut maps based on the ET threshold.
        
        Args:
            threshold (float): The ET threshold for the chain.
        """
        ##########################
        # Et 5 GeV
        ##########################
        # e5_loose1
        ##########################
        # self.HADETthr       = [0.1738, 0.1696, 0.1318, 0.1738, 0.0548875, 0.1486, 0.1696, 0.1738, 0.157]
        # self.CAERATIOthr    = [0.57, 0.532, 0.342, 0.228, -9999., 0.304, 0.608, 0.722, -9999.]
        # self.CARCOREthr     = [0.532, 0.57, 0.646, 0.684, -9999., 0.722, 0.684, 0.722, -9999.]
        ##########################
        # e5_medium1
        #self.HADETthr       = [0.1638, 0.1596, 0.1218, 0.1638, 0.0448875, 0.1386, 0.1596, 0.1638, 0.147]
        #self.CARCOREthr     = [0.532, 0.57, 0.646, 0.684, 0.418, 0.722, 0.684, 0.722, 0.70]
        #self.CAERATIOthr    = [0.57, 0.532, 0.342, 0.228, -9999., 0.304, 0.608, 0.722, -9999.]
        # e5_tight1
        # self.HADETthr        = [0.1638, 0.1596, 0.1218, 0.1638, 0.0448875, 0.1386, 0.1596, 0.1638, 0.147]
        # self.CARCOREthr      = [0.532, 0.57, 0.646, 0.684, 0.418, 0.722, 0.684, 0.722, 0.70]
        # self.CAERATIOthr     = [0.57, 0.532, 0.342, 0.228, -9999., 0.304, 0.608, 0.722, -9999.]
        ##########################
        if(float(threshold) < 12):
            self.MapsHADETthr = {
                    'vloose': [0.2337, 0.20976, 0.1392, 0.1872, 0.1315, 0.3234, 0.384, 0.1901, 0.1901],
                    'loose': [0.2337, 0.2097, 0.1392, 0.1872, 0.1255, 0.3234, 0.3840, 0.1901, 0.1901],
                    'lhvloose': [0.2337, 0.20976, 0.1392, 0.1872, 0.1315, 0.3234, 0.384, 0.1901, 0.1901],
                    'lhloose': [0.2337, 0.2097, 0.1392, 0.1872, 0.1255, 0.3234, 0.3840, 0.1901, 0.1901],
                    'medium': [0.1872, 0.1824, 0.1392, 0.1872, 0.08196 ,0.2497, 0.384, 0.19008, 0.19008],
                    'lhmedium': [0.1872, 0.1824, 0.1392, 0.1872, 0.08196 ,0.2497, 0.384, 0.19008, 0.19008],
                    'tight': [0.1872, 0.1824, 0.1392, 0.1872, 0.06864, 0.24972, 0.31368, 0.1872, 0.168],
                    'lhtight': [0.1872, 0.1824, 0.1392, 0.1872, 0.06864, 0.24972, 0.31368, 0.1872, 0.168],
                    'mergedtight': [0.1872, 0.1824, 0.1392, 0.1872, 0.06864, 0.24972, 0.31368, 0.1872, 0.168],
                    }
            self.MapsCAERATIOthr = {
                    'vloose': [0.48, 0.448, 0.1295, 0.0137, -9999. ,0.0122, 0.512, 0.6073, -9999],
                    'loose': [0.48, 0.448, 0.1295, 0.0137, -9999., 0.0122, 0.512, 0.6073, -9999],
                    'lhvloose': [0.48, 0.448, 0.1295, 0.0137, -9999. ,0.0122, 0.512, 0.6073, -9999],
                    'lhloose': [0.48, 0.448, 0.1295, 0.0137, -9999., 0.0122, 0.512, 0.6073, -9999],
                    'medium': [0.48, 0.448, 0.288, 0.192, -9999., 0.0176, 0.512, 0.608, -9999.],
                    'lhmedium': [0.48, 0.448, 0.288, 0.192, -9999., 0.0176, 0.512, 0.608, -9999.],
                    'tight': [0.48, 0.448, 0.288, 0.192, -9999., 0.256, 0.512, 0.608, -9999.],
                    'lhtight': [0.48, 0.448, 0.288, 0.192, -9999., 0.256, 0.512, 0.608, -9999.],
                    'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                    }
            self.MapsCARCOREthr = {
                    'vloose': [0.448, 0.48, 0.5414, 0.576, 0.352, 0.608, 0.576, 0.608, 0.55],
                    'loose': [0.6806, 0.6710, 0.6306, 0.6619, 0.4704, 0.7094, 0.7012, 0.6977, 0.6960],
                    'lhvloose': [0.448, 0.48, 0.5414, 0.576, 0.352, 0.608, 0.576, 0.608, 0.55],
                    'lhloose': [0.6806, 0.6710, 0.6306, 0.6619, 0.4704, 0.7094, 0.7012, 0.6977, 0.6960],
                    'medium': [0.448, 0.48, 0.544, 0.576, 0.352, 0.608, 0.576, 0.608, 0.598],
                    'lhmedium': [0.448, 0.48, 0.544, 0.576, 0.352, 0.608, 0.576, 0.608, 0.598],
                    'tight': [0.448, 0.48, 0.544, 0.576, 0.352, 0.608, 0.576, 0.608, 0.598],
                    'lhtight': [0.448, 0.48, 0.544, 0.576, 0.352, 0.608, 0.576, 0.608, 0.598],
                    'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                    }
        ##########################
        # Et 12 GeV
        ##########################
        # e12_loose1
        #AT 30-March-2012 Optimisation by Yanping:
        #self.HADETthr      = [0.04225, 0.04075, 0.04575, 0.03575, 0.05275, 0.05325, 0.05525, 0.05325, 0.04675]
        #self.CARCOREthr    = [0.8275, 0.8225, 0.7975, 0.8275, -9999., 0.8075, 0.8475, 0.8475, -9999.]
        #self.CAERATIOthr   = [0.775269, 0.735433, 0.574831, 0.513675, -9999., 0.584799, 0.776095, 0.822032, -9999.]
        #AT: this optimisation could be well propagated to all loose1 triggers with ET>12 GeV if we need to cut L2 rate further
        # e12_medium1
        #self.HADETthr       = [0.04225, 0.04075, 0.04575, 0.03575, 0.05275, 0.05325, 0.05525, 0.05325, 0.04675]
        #self.CARCOREthr     = [0.8275, 0.8225, 0.7975, 0.8275, -9999., 0.8075, 0.8475, 0.8475, -9999.]
        #self.CAERATIOthr   = [0.775269, 0.735433, 0.574831, 0.513675, -9999., 0.584799, 0.776095, 0.822032, -9999.]
        # e12_tight
        # self.HADETthr       = [0.043, 0.043, 0.043, 0.043, 0.043, 0.043, 0.043, 0.043, 0.043]
        # self.CARCOREthr     = [0.90, 0.89, 0.89, 0.89, 0.90, 0.89, 0.89, 0.89, 0.89]
        # self.CAERATIOthr    = [0.60, 0.70, 0.70, 0.75, 0.85, 0.90, 0.90, 0.90, 0.90]
        if(float(threshold) >= 12. and float(threshold) < 22):
            self.MapsHADETthr = { 
                 'vloose':  [0.0871, 0.0617, 0.0564, 0.0827, 0.0889, 0.2052, 0.1674, 0.1481, 0.1481],
                 'loose':  [0.08472, 0.05928, 0.054, 0.0803, 0.0829, 0.1932, 0.1590, 0.1384 , 0.1384],
                 'lhvloose': [0.0871, 0.0617, 0.0564, 0.0827, 0.0889, 0.2052, 0.1674, 0.1481, 0.1481],
                 'lhloose': [0.08472, 0.05928, 0.054, 0.0803, 0.0829, 0.1932, 0.1590, 0.1384 , 0.1384],
                 'medium':  [0.0588, 0.0564, 0.054, 0.048, 0.06384, 0.17868, 0.1284, 0.07536, 0.07536],
                 'lhmedium':  [0.0588, 0.0564, 0.054, 0.048, 0.06384, 0.17868, 0.1284, 0.07536, 0.07536],
                 'tight': [0.0588, 0.0564, 0.054, 0.048, 0.04368, 0.15612, 0.11064, 0.07536, 0.07536],
                 'lhtight': [0.0588, 0.0564, 0.054, 0.048, 0.04368, 0.15612, 0.11064, 0.07536, 0.07536],
                 'mergedtight': [0.0588, 0.0564, 0.054, 0.048, 0.04368, 0.15612, 0.11064, 0.07536, 0.07536],
                 }
            self.MapsCARCOREthr = {
                    'vloose': [0.6646, 0.6590, 0.6226, 0.6539, 0.4704, 0.6536, 0.6972, 0.6817, 0.672],
                    'loose': [0.6806, 0.6710, 0.6306, 0.6619, 0.4704, 0.6616, 0.7012, 0.6977, 0.696],
                    'lhvloose': [0.6646, 0.6590, 0.6226, 0.6539, 0.4704, 0.6536, 0.6972, 0.6817, 0.672],
                    'lhloose': [0.6806, 0.6710, 0.6306, 0.6619, 0.4704, 0.6616, 0.7012, 0.6977, 0.696],
                    'medium': [0.69896, 0.68416, 0.64368, 0.68488, 0.4704, 0.6816, 0.704, 0.6992, 0.6992],
                    'lhmedium': [0.69896, 0.68416, 0.64368, 0.68488, 0.4704, 0.6816, 0.704, 0.6992, 0.6992],
                    'tight': [0.71296, 0.69344, 0.64368, 0.69064, 0.4704, 0.7036, 0.73024, 0.7164, 0.7164],
                    'lhtight': [0.71296, 0.69344, 0.64368, 0.69064, 0.4704, 0.7036, 0.73024, 0.7164, 0.7164],
                    'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                    }
            self.MapsCAERATIOthr = {
                    'vloose': [0.5702, 0.6063, 0.4418, 0.4257, -9999. , 0.3408, 0.5836, 0.6800, -999],
                    'loose': [0.5702, 0.6063, 0.4418, 0.4257, -9999., 0.3408, 0.5836, 0.6800, -999],
                    'lhvloose': [0.5702, 0.6063, 0.4418, 0.4257, -9999. , 0.3408, 0.5836, 0.6800, -999],
                    'lhloose': [0.5702, 0.6063, 0.4418, 0.4257, -9999., 0.3408, 0.5836, 0.6800, -999],
                    'medium': [0.636,  0.6064,  0.5552,  0.476,  -9999.,  0.5536,  0.664,  0.68 , -9999.],
                    'lhmedium': [0.636,  0.6064,  0.5552,  0.476,  -9999.,  0.5536,  0.664,  0.68 , -9999.],
                    'tight': [0.636, 0.652,  0.5552, 0.4768, -9999.,  0.6056, 0.6696, 0.7128, -9999.],
                    'lhtight': [0.636, 0.652,  0.5552, 0.4768, -9999.,  0.6056, 0.6696, 0.7128, -9999.],
                    'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                    }
        ##########################
        # Et 22 GeV
        ##########################
        # e24_medium1 / e24_tight1
        # AT 30-March-2012 Optimisation by Yanping:
        # self.HADETthr      = [0.0256693, 0.0240023, 0.0271098, 0.0206744, 0.0211902, 0.0301758, 0.0297629, 0.0295336, 0.020514]
        # self.CARCOREthr     = [0.882167, 0.882156, 0.857124, 0.886262, 0.724005, 0.871725, 0.902082, 0.887027, 0.744103]
        # self.CAERATIOthr    = [0.83009, 0.830144, 0.794944, 0.794558, -9999, 0.794933, 0.895365, 0.904011, -9999.]
        # e24_loose1
        # self.CAERATIOthr    = [-999., -999., -999., -999., -999., -999., -999., -999., -999.]
        # self.HADETthr      = [0.0275625, 0.0259875, 0.0291375, 0.0228375, 0.0259875, 0.0391125, 0.0359625, 0.0370125, 0.0291375]
        # self.CARCOREthr = [0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625]
        if(float(threshold) >= 22.):
             self.MapsHADETthr = {       
                 'vloose':  [0.0612, 0.0588, 0.0564, 0.0504, 0.0357, 0.072, 0.0684, 0.0696, 0.0636],
                 'loose':  [0.0588, 0.0564, 0.054, 0.048, 0.0297, 0.06, 0.06, 0.06, 0.054],
                 'lhvloose':  [0.0612, 0.0588, 0.0564, 0.0504, 0.0357, 0.072, 0.0684, 0.0696, 0.0636],
                 'lhloose':  [0.0588, 0.0564, 0.054, 0.048, 0.0297, 0.06, 0.06, 0.06, 0.054],
                 'medium': [0.0588, 0.0564, 0.054, 0.048, 0.02376, 0.06, 0.06, 0.06, 0.054],
                 'lhmedium': [0.0588, 0.0564, 0.054, 0.048, 0.02376, 0.06, 0.06, 0.06, 0.054],
                 'tight':  [0.0588, 0.0564, 0.054, 0.048, 0.02376, 0.06, 0.06, 0.06, 0.054],
                 'lhtight':  [0.0588, 0.0564, 0.054, 0.048, 0.02376, 0.06, 0.06, 0.06, 0.054],
                 'mergedtight':  [0.0588, 0.0564, 0.054, 0.048, 0.02376, 0.06, 0.06, 0.06, 0.054],
                 }
             self.MapsCARCOREthr = {
                  'vloose': [0.6912 , 0.6808 , 0.6832 , 0.6744 , 0.5976 , 0.6416, 0.692  , 0.6848 , 0.68],
                  'loose': [0.7112, 0.6968, 0.6952, 0.6864, 0.5976, 0.6616, 0.704 , 0.7008, 0.696],
                  'lhvloose': [0.6912 , 0.6808 , 0.6832 , 0.6744 , 0.5976 , 0.6416, 0.692  , 0.6848 , 0.68],
                  'lhloose': [0.7112, 0.6968, 0.6952, 0.6864, 0.5976, 0.6616, 0.704 , 0.7008, 0.696],
                  'medium': [0.716, 0.712, 0.6952, 0.692, 0.5976, 0.6816, 0.7168, 0.7128, 0.716],
                  'lhmedium': [0.716, 0.712, 0.6952, 0.692, 0.5976, 0.6816, 0.7168, 0.7128, 0.716],
                  'tight': [0.7288, 0.7296, 0.72, 0.7048, 0.6, 0.7128, 0.7312, 0.7256, 0.7192],
                  'lhtight': [0.7288, 0.7296, 0.72, 0.7048, 0.6, 0.7128, 0.7312, 0.7256, 0.7192],
                  'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                  }
             self.MapsCAERATIOthr = {
                    'vloose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                    'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                    'lhvloose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                    'lhloose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                    'medium': [0.656, 0.66, 0.6, 0.604, -9999., 0.624, 0.664, 0.692, -9999.],
                    'lhmedium': [0.656, 0.66, 0.6, 0.604, -9999., 0.624, 0.664, 0.692, -9999.],
                    'tight': [0.72, 0.712, 0.68, 0.672, -9999., 0.68, 0.716, 0.74, -9999.],
                    'lhtight': [0.72, 0.712, 0.68, 0.672, -9999., 0.68, 0.716, 0.74, -9999.],
                    'mergedtight': [-9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999., -9999.],
                    }

# Following is much easier, no Et dependence
# Almost no dependence on PID
class L2CaloPhotonCutMaps:
    """
    Cut maps for L2 Calorimeter photon hypo.
    
    This class defines the HADET, CAERATIO, and CARCORE threshold maps
    grouped by Et threshold and selection level for photons.
    
    Attributes:
        MapsHADETthr (dict): Map of HADET threshold lists per selection level.
        MapsCAERATIOthr (dict): Map of CAERATIO threshold lists per selection level.
        MapsCARCOREthr (dict): Map of CARCORE threshold lists per selection level.
    """
    def __init__(self, threshold: float) -> None:
        """
        Initialize cut maps based on the ET threshold.
        
        Args:
            threshold (float): The ET threshold for the chain.
        """
        if(float(threshold) >= 0. and float(threshold) < 10):
            self.MapsHADETthr = {
                'loose': [0.1638, 0.1596, 0.1218, 0.1638, 0.0448875, 0.1386, 0.1596, 0.1638, 0.147],
                'medium':[0.0254625, 0.0238875, 0.0270375, 0.0207375, 0.03465, 0.0378, 0.03465, 0.0286125, 0.02625],
                'tight':[0.0254625, 0.0238875, 0.0270375, 0.0207375, 0.03465, 0.0378, 0.03465, 0.0286125, 0.02625],
                }
            self.MapsCARCOREthr = {
                'loose': [0.532, 0.57, 0.646, 0.684, 0.418, 0.722, 0.684, 0.722, 0.76],
                'medium':[0.83125, 0.719625, 0.814625, 0.83125, 0.703, 0.817, 0.83125, 0.8265, 0.719625],
                'tight':[0.83125, 0.719625, 0.814625, 0.83125, 0.703, 0.817, 0.83125, 0.8265, 0.719625],
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        elif(float(threshold) >= 10. and float(threshold) < 15):
            self.MapsHADETthr = {
                'loose': [0.0359625, 0.0343875, 0.0396375, 0.0291375, 0.0501375, 0.0559125, 0.0548625, 0.0538125, 0.0469875],
                'medium':[0.0359625, 0.0343875, 0.0396375, 0.0291375, 0.0501375, 0.0559125, 0.0548625, 0.0538125, 0.0469875],
                'tight':[0.0359625, 0.0343875, 0.0396375, 0.0291375, 0.0501375, 0.0559125, 0.0548625, 0.0538125, 0.0469875],
                }
            self.MapsCARCOREthr = {
                'loose': [0.786125, 0.786125, 0.767125, 0.795625, 0.703, 0.776625, 0.819375, 0.805125, 0.681625],
                'medium':[0.786125, 0.786125, 0.767125, 0.795625, 0.703, 0.776625, 0.819375, 0.805125, 0.681625],
                'tight':[0.786125, 0.786125, 0.767125, 0.795625, 0.703, 0.776625, 0.819375, 0.805125, 0.681625],
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        elif(float(threshold) >= 15. and float(threshold) < 20):
            self.MapsHADETthr = {
                'loose':[0.0328125, 0.0312375, 0.0354375, 0.0270375, 0.0459375, 0.0527625, 0.0433125, 0.0485625, 0.0396375], 
                'medium':[0.0328125, 0.0312375, 0.0354375, 0.0270375, 0.0459375, 0.0527625, 0.0433125, 0.0485625, 0.0396375], 
                'tight':[0.0328125, 0.0312375, 0.0354375, 0.0270375, 0.0459375, 0.0527625, 0.0433125, 0.0485625, 0.0396375], 
                }
            self.MapsCARCOREthr = {
                'loose':[0.809875, 0.805125, 0.786125, 0.809875, 0.703, 0.795625, 0.819375, 0.814625, 0.691125], 
                'medium':[0.809875, 0.805125, 0.786125, 0.809875, 0.703, 0.795625, 0.819375, 0.814625, 0.691125], 
                'tight':[0.809875, 0.805125, 0.786125, 0.809875, 0.703, 0.795625, 0.819375, 0.814625, 0.691125], 
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        elif(float(threshold) >= 20. and float(threshold) < 30):
            self.MapsHADETthr = {
                'loose':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'medium':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'tight':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                }
            self.MapsCARCOREthr = {
                'loose':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'medium':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'tight':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        elif(float(threshold) >= 30. and float(threshold) < 40):
            self.MapsHADETthr = {
                'loose':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'medium':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'tight':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                }
            self.MapsCARCOREthr = {
                'loose':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'medium':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'tight':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium':[-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        elif(float(threshold) >= 40.):
            self.MapsHADETthr = {
                'loose':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'medium':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                'tight':[0.071, 0.062, 0.075, 0.060, 0.051, 0.057, 0.075, 0.072, 0.051],
                }
            self.MapsCARCOREthr = {
                'loose':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'medium':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                'tight':[0.819375, 0.819375, 0.800375, 0.828875, 0.7125, 0.805125, 0.843125, 0.824125, 0.700625],
                }
            self.MapsCAERATIOthr = {
                'loose': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'medium': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                'tight': [-999., -999., -999., -999., -999., -999., -999., -999., -999.],
                }
        else:
             raise RuntimeError('INCORRECT threshold: No cuts configured')     

