
import math

__all__ = [
    "MeV", "GeV",
    "eta_bins_default", "zee_et_bins", "mu_bins",
    "ring_lower_edges", "ring_high_edges", "ring_nbins",
    "coarse_et_bins", "jpsiee_et_bins", "nvtx_bins", "high_nvtx_bins",
    "ringer_tuning_et_bins", "ringer_tuning_eta_bins",
    "lh_tuning_et_bins", "lh_tuning_eta_bins",
    "lh_thres_et_bins", "lh_thres_eta_bins",
    "n_eta_lh_tuning", "n_et_lh_tuning",
    "standard_quantities_special_bins", "standard_quantities_eta_edge",
    "standard_quantities_lower_edges", "standard_quantities_high_edges", "standard_quantities_nbins",
    "standard_quantities_pdfs_lower_edges", "standard_quantities_pdfs_high_edges", "standard_quantities_pdfs_nbins",
    "special_electron_bins", "basic_info_nbins", "basic_info_lower_edges", "basic_info_high_edges",
    "electron_quantities", "basic_info_quantities",
    "get_electron_latex_str", "get_basic_info_latex_str"
]

# Physical units and conversion factors
MeV = 1.0
GeV = 1000.0

# --- Default Binning Edges ---

# Standard eta bins for EGamma analysis
eta_bins_default = [
    -2.47, -2.37, -2.01, -1.81, -1.52, -1.37, -1.15, -0.80, -0.60, -0.10, 0.00,
    0.10, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47
]

# Alternative eta bins used in some fitting procedures
etabins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]

# Standard Et bins for Zee analysis
zee_et_bins = [
    0., 2., 4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24., 26., 28.,
    30., 32., 34., 36., 38., 40., 42., 44., 46., 48., 50., 55., 60., 65., 70., 100.
]

# Standard Et bins for Jpsi to ee analysis
jpsiee_et_bins = [
    0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5,
    8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0
]

# Coarse Et bins for general performance studies
coarse_et_bins = [4., 7., 10., 15., 20., 25., 30., 35., 40., 45., 50., 60., 80., 150.]

# Standard pileup (mu) bins
mu_bins = [0, 20, 40, 60, 80, 100]

# Number of primary vertices bins (standard and high pileup)
nvtx_bins = [
    -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5,
    10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5,
    20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5, 27.5, 28.5, 29.5,
    30.5, 31.5, 32.5, 33.5, 34.5, 35.5, 36.5, 37.5, 38.5, 39.5,
    40.5, 41.5, 42.5, 43.5, 44.5, 45.5, 46.5, 47.5, 48.5, 49.5,
    50.5, 51.5, 52.5, 53.5, 54.5, 55.5, 56.5, 57.5, 58.5, 59.5, 60.5
]

high_nvtx_bins = [
    61.5, 62.5, 63.5, 64.5, 65.5, 66.5, 67.5, 68.5, 69.5, 70.5,
    71.5, 72.5, 73.5, 74.5, 75.5, 76.5, 77.5, 78.5, 79.5, 80.5,
    81.5, 82.5, 83.5, 84.5, 85.5, 86.5, 87.5, 88.5, 89.5, 90.5,
    91.5, 92.5, 93.5, 94.5, 95.5, 96.5, 97.5, 98.5, 99.5, 100.5
]

# --- Ringer Calorimeter Rings Binning ---

# Lower edges for the 100 rings (PS, EM1, EM1, EM1, EM1, EM1, EM1, EM1, EM1, EM2, EM3, HAD1, HAD2, HAD3)
ring_lower_edges = [
    -1000., -1000., -1000., -1000., -1000., -1000., -1000., -900.,   # PS
    -2500., -2500., -1500., -1500., -1500., -1500., -2000., -2000.,  # EM1
    -2000., -2000., -800.,  -800.,  -800.,  -800.,  -800.,  -800.,   # EM1
    -800.,  -800.,  -800.,  -800.,  -800.,  -800.,  -800.,  -700.,   # EM1
    -600.,  -600.,  -600.,  -600.,  -600.,  -600.,  -600.,  -600.,   # EM1
    -600.,  -600.,  -600.,  -500.,  -500.,  -500.,  -500.,  -500.,   # EM1
    -500.,  -500.,  -500.,  -500.,  -500.,  -400.,  -400.,  -400.,   # EM1
    -400.,  -400.,  -400.,  -400.,  -400.,  -400.,  -300.,  -300.,   # EM1
    -300.,  -300.,  -300.,  -300.,  -300.,  -300.,  -300.,  -300.,   # EM1
    -1000., -1000., -1000., -1500., -2000., -2000., -2000., -2000.,  # EM2
    -900.,  -900.,  -900.,  -900.,  -900.,  -900.,  -800.,  -800.,   # EM3
    -3000., -3000., -3000., -3000.,                                 # HAD1
    -2000., -2000., -2000., -2000.,                                 # HAD2
    -1000., -1000., -1000., -1000.                                  # HAD3
]

# High edges for the 100 calorimeter rings
ring_high_edges = [
    14000., 14000., 8000.,  7000.,  6500.,  6000., 5500., 5000. ,  # PS
    17000., 15000., 12000., 9000.,  9000.,  7000., 6500., 5500. ,  # EM1
    8500.,  5000.,  5000.,  5000.,  5000.,  4500., 4500., 4500. ,  # EM1
    4000.,  4000.,  4000.,  4000.,  4000.,  3500., 3500., 3500. ,  # EM1
    3500.,  3500.,  3500.,  3500.,  3500.,  3500., 3500., 3500. ,  # EM1
    3500.,  3500.,  3500.,  3000.,  3000.,  3000., 3000., 3000. ,  # EM1
    3000.,  3000.,  3000.,  3000.,  2500.,  2500., 2500., 2500. ,  # EM1
    2500.,  2500.,  2500.,  2200.,  2200.,  2200., 2200., 2200. ,  # EM1
    2200.,  2200.,  2200.,  2200.,  2200.,  2000., 2000., 2000. ,  # EM1
    80000., 80000., 40000., 25000., 18000., 18000., 12500., 12000., # EM2
    14000., 12000., 8000.,  7000.,  5000.,  4500., 4200., 4000. ,  # EM3
    60000., 60000., 30000., 22000. ,                                # HAD1
    60000., 60000., 25000., 20000. ,                                # HAD2
    25000., 30000., 15000., 12000.                                  # HAD3
]

# Standard number of bins for rings (historically 60)
ring_nbins = [60] * 100

# --- Tuning and Threshold Binning ---

# Ringer tuning bins (Run 2/3)
ringer_tuning_et_bins = [15, 20, 30, 40, 50, 1e5]
ringer_tuning_eta_bins = [0, 0.8, 1.37, 1.54, 2.37, 2.47]

# Likelihood (LH) tuning bins
lh_tuning_et_bins = [4, 7, 10, 15, 20, 30, 40, 50000]
lh_tuning_eta_bins = [0.00, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]

# LH Threshold bins
lh_thres_et_bins = [4, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50, 50000]
lh_thres_eta_bins = [0.00, 0.60, 0.80, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]

# Derived dimensions for LH tuning
n_eta_lh_tuning = len(lh_tuning_eta_bins) - 1
n_et_lh_tuning = len(lh_tuning_et_bins) - 1

# --- EGamma Shower Shapes and Track Variables ---

# Special binning for specific variables in histograms
standard_quantities_special_bins = {
    "f1": [0.],
    "f3": [0.],
    "reta": [1.],
    "rphi": [1.],
    "eratio": [0., 1.],
    "TRT_PID": [0.],
    "deltaPoverP": [0.]
}

# Eta edges for variables that only exist in certain regions
standard_quantities_eta_edge = {
    "f3": 2.37,
    "TRT_PID": 2.01
}

# Default lower edges for shower shapes and tracking variables
standard_quantities_lower_edges = {
    "f1": -0.02,
    "f3": -0.05,
    "weta2": 0.005,
    "wtots1": 0.00,
    "reta": 0.80,
    "rhad": -0.05,
    "rphi": 0.45,
    "eratio": 0.50,
    "deltaEta1": -0.01,
    "deltaPhiRescaled2": -0.03,
    "trackd0pvunbiased": -0.50,
    "d0significance": 0.00,
    "eProbabilityHT": -0.05,
    "TRT_PID": -1.00,
    "DeltaPOverP": -1.2,
}

# Default high edges for shower shapes and tracking variables
standard_quantities_high_edges = {
    "f1": 0.7,
    "f3": 0.15,
    "weta2": 0.02,
    "wtots1": 8.00,
    "reta": 1.10,
    "rhad": 0.05,
    "rphi": 1.05,
    "eratio": 1.05,
    "deltaEta1": 0.01,
    "deltaPhiRescaled2": 0.03,
    "trackd0pvunbiased": 0.50,
    "d0significance": 10.00,
    "eProbabilityHT": 1.05,
    "TRT_PID": 1.00,
    "DeltaPOverP": 1.2,
}

# Default number of bins for shower shapes and tracking variables
standard_quantities_nbins = {
    "f1": 100,
    "f3": 200,
    "weta2": 100,
    "wtots1": 100,
    "reta": 200,
    "rhad": 200,
    "rphi": 200,
    "eratio": 100,
    "deltaEta1": 200,
    "deltaPhiRescaled2": 200,
    "trackd0pvunbiased": 200,
    "d0significance": 100,
    "eProbabilityHT": 100,
    "TRT_PID": 100,
    "DeltaPOverP": 100,
}

# --- PDF Binning Edges (for likelihood calculation) ---

standard_quantities_pdfs_lower_edges = {
    "deltaEmax2": [[0.] * 9] * 7,
    "eratio": [[0.] * 9] * 7,
    "weta2": [[0.006] * 9] * 7,
    "ws3": [[0.3] * 9] * 7,
    "deltaEta1": [[-0.1] * n_eta_lh_tuning] * n_et_lh_tuning,
    "f1": [[-0.05] * n_eta_lh_tuning] * n_et_lh_tuning,
    "f3": [[-0.02] * n_eta_lh_tuning] * n_et_lh_tuning,
    "fside": [[-0.2] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaPhi2": [[-0.1] * n_eta_lh_tuning] * n_et_lh_tuning,
    "reta": [[0.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "rhad": [[-0.075] * n_eta_lh_tuning] * n_et_lh_tuning,
    "rphi": [[0.45] * n_eta_lh_tuning] * n_et_lh_tuning,
    "wstot": [[0.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "d0significance": [[0.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRTHighTHitsRatio": [[0.0] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRTHighTOutliersRatio": [[0.0] * n_eta_lh_tuning] * n_et_lh_tuning,
    "trackd0pvunbiased": [[-1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaPoverP": [[-0.2] * n_eta_lh_tuning] * n_et_lh_tuning,
    "ptcone20pt": [[0.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "EoverP": [[0.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "PassBL": [[0.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaphiRescaled": [[-0.150] * n_eta_lh_tuning] * n_et_lh_tuning,
}

# (Updating specific PDF edges as found in the old source)
standard_quantities_pdfs_lower_edges["deltaEmax2"] = [
    [0., 0., 0., 0., 0., 0., 0.5, 0.8, 0.], [0., 0., 0., 0., 0., 0., 0.5, 0.8, 0.],
    [0., 0., 0., 0., 0., 0., 0.5, 0.8, 0.], [0., 0., 0., 0., 0., 0., 0.5, 0.8, 0.],
    [0., 0., 0., 0., 0., 0., 0.8, 0.8, 0.], [0., 0., 0., 0., 0., 0., 0.8, 0.85, 0.],
    [0., 0., 0., 0., 0., 0., 0.8, 0.85, 0.]]
standard_quantities_pdfs_lower_edges["eratio"] = standard_quantities_pdfs_lower_edges["deltaEmax2"]
standard_quantities_pdfs_lower_edges["weta2"] = [[0.006, 0.006, 0.006, 0.006, 0.00, 0.006, 0.006, 0.006, 0.006]] * 7
standard_quantities_pdfs_lower_edges["ws3"] = [[0.3, 0.3, 0.3, 0.3, 0.00, 0.3, 0.3, 0.3, 0.3]] * 7


standard_quantities_pdfs_high_edges = {
    "f1": [[0.65, 0.6, 0.5, 0.5, 0.55, 0.55, 0.55, 0.65, 0.5]] * 7,
    "weta2": [[0.018, 0.018, 0.018, 0.018, 0.030, 0.018, 0.018, 0.018, 0.018]] * 7,
    "ws3": [[1., 1., 1., 1., 1., 1., 1., 1., 1.]] * 7,
    "deltaeta1": [[0.1] * n_eta_lh_tuning] * n_et_lh_tuning,
    "f3": [[0.15] * n_eta_lh_tuning] * n_et_lh_tuning,
    "fside": [[1.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaphi2": [[0.05] * n_eta_lh_tuning] * n_et_lh_tuning,
    "reta": [[1.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "rhad": [[0.2] * n_eta_lh_tuning] * n_et_lh_tuning,
    "rphi": [[1.05] * n_eta_lh_tuning] * n_et_lh_tuning,
    "wstot": [[8.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "d0Sig": [[20.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "d0significance": [[20.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRTHighTHitsRatio": [[0.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRTHighTOutliersRatio": [[0.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "trackd0": [[1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "trackd0_physics": [[1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "trackd0pvunbiased": [[1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaEmax2": [[1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "eratio": [[1.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "ptcone20pt": [[0.5] * n_eta_lh_tuning] * n_et_lh_tuning,
    "EoverP": [[8.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "PassBL": [[2.] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaphiRescaled": [[0.150] * n_eta_lh_tuning] * n_et_lh_tuning,
    "deltaPoverP": [[1.0] * n_eta_lh_tuning] * n_et_lh_tuning,
    "eProbabilityHT": [[1] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRT_PID": [[0.96] * n_eta_lh_tuning] * n_et_lh_tuning,
    "TRT_PID_significance": [[0.3] * n_eta_lh_tuning] * n_et_lh_tuning,
}

standard_quantities_pdfs_nbins = {
    "deltaeta1": 500, "f3": 500, "fside": 500,
    "deltaphi2": 500, "reta": 500, "rhad": 500,
    "rphi": 500, "wstot": 500, "d0Sig": 500,
    "d0significance": 500, "TRTHighTHitsRatio": 60, "TRTHighTOutliersRatio": 60,
    "trackd0": 500, "trackd0_physics": 500, "trackd0pvunbiased": 500,
    "ptcone20pt": 500, "EoverP": 500, "PassBL": 500,
    "deltaphiRescaled": 500, "deltaPoverP": 500, "MVAResponse": 500,
    "cl_phi": 500, "eProbabilityHT": 500, "TRT_PID": 500,
    "TRT_PID_significance": 500, "deltaEmax2": 500, "eratio": 500,
    "f0": 500, "f1": 500, "weta2": 500, "ws3": 500,
}

# --- Event and Quantities Labels ---

# Special binning for electron identification variables
special_electron_bins = {
    'f1': [0], 'f3': [0], 'reta': [1], 'rphi': [1], 'eratio': [0, 1],
    'TRT_PID': [0], 'deltaPOverP': [0]
}

# Generic histogram booking parameters
basic_info_nbins = {"et": 100, "eta": 100, "phi": 100, "avgmu": 62, "nvtx": 62}
basic_info_lower_edges = {"et": 0, "eta": -2.5, "phi": -math.pi, "avgmu": -0.5, "nvtx": -0.5}
basic_info_high_edges = {"et": 100, "eta": 2.5, "phi": math.pi, "avgmu": 60.5, "nvtx": 60.5}

# LaTeX labels for electron variables (for plotting)
electron_quantities = {
    'et': 'E_{T}', 'eta': '#eta', 'phi': '#phi', 'rhad': 'R_{had}', 'reta': 'R_{#eta}',
    'deltaEta1': '#Delta#eta_{1}', 'weta2': 'w_{#eta,2}', 'wtots1': 'w_{tots,1}',
    'f1': 'f_{1}', 'rphi': 'R_{#phi}', 'f3': 'f_{3}', 'eratio': 'E_{ratio}',
    'deltaPhiRescaled2': '#Delta#phi_{res}', 'd0significance': 'd_{0}/#sigma_{d_{0}}',
    'trackd0pvunbiased': 'd_{0}', 'eProbabilityHT': 'eProbabilityHT',
    'TRT_PID': 'TRT_{PID}', 'DeltaPOverP': '#Delta p/p'
}

def get_electron_latex_str(var: str) -> str:
    """Returns the LaTeX representation of an electron quantity."""
    try:
        return electron_quantities[var]
    except KeyError:
        raise KeyError(f'Latex string is unavailable for quantity: {var}')

# LaTeX labels for basic event variables
basic_info_quantities = {
    'et': 'E_{T}', 'eta': '#eta', 'phi': '#phi', 'avgmu': '<#mu>',
    'nvtx': '# Primary Vertices'
}

def get_basic_info_latex_str(var: str) -> str:
    """Returns the LaTeX representation of a basic event quantity."""
    try:
        return basic_info_quantities[var]
    except KeyError:
        raise KeyError(f'Latex string is unavailable for quantity: {var}')
