
__all__ = ["Quadrant", "QuadrantConfig"]

import math
import array
import numpy as np
from typing import List, Dict, Optional, Sequence, Any, Union, Tuple
from ROOT import TH1F, TH2F, TProfile, TProfile2D

from trig_egamma_frame.kernel import Algorithm, StatusCode, EventContext
from trig_egamma_frame import logger, GeV
from trig_egamma_frame.enumerators import DataframeType as DataframeEnum
from trig_egamma_frame.constants import (
    eta_bins_default as default_etabins,
    basic_info_quantities,
    basic_info_nbins,
    basic_info_lower_edges,
    basic_info_high_edges,
    electron_quantities,
    standard_quantities_nbins,
    standard_quantities_lower_edges,
    standard_quantities_high_edges,
    nvtx_bins,
    lh_tuning_et_bins,
    lh_tuning_eta_bins,
)


class QuadrantConfig:
    """Config for a quadrant feature (pair of trigger expressions)."""
    def __init__(self, name_a: str, expression_a: str, name_b: str, expression_b: str):
        self._name_a = name_a
        self._expression_a = expression_a
        self._name_b = name_b
        self._expression_b = expression_b
    
    def name_a(self) -> str: return self._name_a
    def expression_a(self) -> str: return self._expression_a
    def name_b(self) -> str: return self._name_b
    def expression_b(self) -> str: return self._expression_b







class Quadrant(Algorithm):
    """
    Algorithm to perform quadrant analysis (passed/rejected comparisons) between trigger pairs.
    """

    def __init__(self, 
                 name: str, 
                 basepath: str = "quadrant",
                 et_bins: List[float] = lh_tuning_et_bins,
                 eta_bins: List[float] = lh_tuning_eta_bins):
        """
        Constructor.

        Args:
            name (str): Algorithm name.
            basepath (str): Base path for histograms.
            et_bins (List[float]): Et bin edges.
            eta_bins (List[float]): Eta bin edges.
        """
        super().__init__(name)
        self.basepath = basepath
        self.et_bins = et_bins
        self.eta_bins = eta_bins
        self.__quadrant_features: List[QuadrantConfig] = []
        self.__quadrants = ['passed_passed', 'passed_rejected', 'rejected_passed', 'rejected_rejected']


    def add_feature(self, name_a: str, name_b: str) -> None:
        """Add a quadrant configuration to monitor."""
        self.__quadrant_features.append((name_a, name_b))


    def initialize(self) -> StatusCode:
        """Initialize histograms."""
        logger.info(f"Initializing {self.name()}...")
        sg = self.getStoreGateSvc()

        etabs = default_etabins

        for feat in self.__quadrant_features:
            quadrant_name = f"{feat[0]}_Vs_{feat[1]}"

            for etBinIdx in range(len(self.et_bins) - 1):
                for etaBinIdx in range(len(self.eta_bins) - 1):
                    for quadrant in self.__quadrants:
                        binning_name = f"et{etBinIdx}_eta{etaBinIdx}"
                        dirname = f"{self.basepath}/{quadrant_name}/{binning_name}/{quadrant}"
                        sg.mkdir(dirname)
                        
                        sg.addHistogram(TH1F('et', f"{basic_info_quantities['et']};{basic_info_quantities['et']};Count",
                                             basic_info_nbins['et'], basic_info_lower_edges['et'], basic_info_high_edges['et']))
                        sg.addHistogram(TH1F('eta', f"{basic_info_quantities['eta']};{basic_info_quantities['eta']};Count",
                                             len(etabs)-1, np.array(etabs)))
                        sg.addHistogram(TH1F('phi', f"{basic_info_quantities['phi']};{basic_info_quantities['phi']};Count", 20, -3.2, 3.2))
                        sg.addHistogram(TH1F('avgmu', f"{basic_info_quantities['avgmu']};{basic_info_quantities['avgmu']};Count", 16, 0, 80))
                        sg.addHistogram(TH1F('nvtx', f"{basic_info_quantities['nvtx']};{basic_info_quantities['nvtx']};Count",
                                             len(nvtx_bins)-1, np.array(nvtx_bins)))

                        for key in standard_quantities_nbins.keys():
                            sg.addHistogram(TH1F(key, 
                                                 f"{electron_quantities[key]};{electron_quantities[key]};Count",
                                                 standard_quantities_nbins[key],
                                                 standard_quantities_lower_edges[key],
                                                 standard_quantities_high_edges[key]))

        self.init_lock()
        return StatusCode.SUCCESS


    def execute(self, context: EventContext) -> StatusCode:
        """Execute per event."""

        sg = self.getStoreGateSvc()
        # Retrieve container
        eg = context.getHandler("ElectronContainer")
        evt = context.getHandler("EventInfoContainer")
        eta = math.fabs(eg.eta())
        et = eg.et() / GeV
        dec = context.getHandler("MenuContainer")


        etBinIdx, etaBinIdx = self.__get_bin(et, eta)        
        if etBinIdx == -1 or etaBinIdx == -1:
            return StatusCode.SUCCESS
        
        binning_name = f"et{etBinIdx}_eta{etaBinIdx}"

        for feat in self.__quadrant_features:
            name     = f"{feat[0]}_Vs_{feat[1]}"
            passed_a = "passed" if dec.accept(feat[0]) else "rejected"
            passed_b = "passed" if dec.accept(feat[1]) else "rejected"
            dirname  = f"{self.basepath}/{name}/{binning_name}/{passed_a}_{passed_b}"

            pw = 1
            # Fill basic infos
            sg.histogram(f"{dirname}/et").Fill(et, pw)
            sg.histogram(f"{dirname}/eta").Fill(eg.eta(), pw)
            sg.histogram(f"{dirname}/phi").Fill(eg.phi(), pw)
            sg.histogram(f"{dirname}/avgmu").Fill(evt.avgmu(), pw)
            sg.histogram(f"{dirname}/nvtx").Fill(evt.nvtx(), pw)
            # Fill shower shapes
            sg.histogram(f"{dirname}/f1").Fill(eg.f1(), pw)
            sg.histogram(f"{dirname}/f3").Fill(eg.f3(), pw)
            sg.histogram(f"{dirname}/weta2").Fill(eg.weta2(), pw)
            sg.histogram(f"{dirname}/wtots1").Fill(eg.wtots1(), pw)
            sg.histogram(f"{dirname}/reta").Fill(eg.reta(), pw)
            sg.histogram(f"{dirname}/rhad").Fill(eg.rhad(), pw)
            sg.histogram(f"{dirname}/rphi").Fill(eg.rphi(), pw)
            sg.histogram(f"{dirname}/eratio").Fill(eg.eratio(), pw)
            sg.histogram(f"{dirname}/deltaEta1").Fill(eg.deltaEta1(), pw)
            sg.histogram(f"{dirname}/deltaPhiRescaled2").Fill(eg.deltaPhiRescaled2(), pw)
            
            # Fill track variables
            track = eg.trackParticle()
            if track:
                sg.histogram(f"{dirname}/trackd0pvunbiased").Fill(track.d0(), pw)
                sg.histogram(f"{dirname}/d0significance").Fill(track.d0significance(), pw)
                sg.histogram(f"{dirname}/eProbabilityHT").Fill(track.eProbabilityHT(), pw)
                sg.histogram(f"{dirname}/TRT_PID").Fill(track.trans_TRT_PID(), pw)
                sg.histogram(f"{dirname}/DeltaPOverP").Fill(track.DeltaPOverP(), pw)

        return StatusCode.SUCCESS


    def finalize(self) -> StatusCode:
        """Finalize."""
        self.fina_lock()
        return StatusCode.SUCCESS



    def __get_bin(self, et: float, eta: float) -> Tuple[int, int]:
        """
        Returns an etBinIdx and etaBinIdx pair given certain et and eta values.

        Uses numpy.digitize for efficient bin lookup.

        Parameters
        ----------
        et : Number
            Transverse energy value
        eta : Number
            Pseudorapidity value

        Returns
        -------
        Tuple[int, int]
            etBinIdx, etaBinIdx values. Returns (-1, -1) if outside ranges.
        """
        et_idx = np.digitize(et, self.et_bins) - 1
        eta_idx = np.digitize(eta, self.eta_bins) - 1

        # Check if indices are within the valid bin range [0, N-1]
        if not (0 <= et_idx < len(self.et_bins) - 1):
            et_idx = -1
        if not (0 <= eta_idx < len(self.eta_bins) - 1):
            eta_idx = -1

        if et_idx == -1 or eta_idx == -1:
            return -1, -1

        return int(et_idx), int(eta_idx)
