from numbers import Number
import ROOT
from array import array
import rootplotlib as rpl
from typing import Union, Tuple, Literal


def parse_bin(
        bin_value: Union[int, Literal['lowest', 'highest']],
        rdf: ROOT.RDataFrame,
        var_name: str) -> Number:
    """
    Parse the bin value to be used in the histogram.
    With the exception of 'lowest' and 'highest', the bin value is expected to
    be an integer.

    Parameters
    ----------
    bin_value : Union[int, Literal['lowest', 'highest']]
        The value to be parsed.
    rdf : ROOT.RDataFrame
        The RDataFrame to be used to get the lowest and highest values.
    var_name : str
        The name of the variable to be used to get the lowest and highest
        values.

    Returns
    -------
    Number
        The parsed bin value.
    """
    if bin_value == 'lowest':
        return rdf.Min(var_name).GetValue()
    elif bin_value == 'highest':
        return rdf.Max(var_name).GetValue()
    else:
        return int(bin_value)


def as_density(hist: ROOT.TH1, inplace: bool) -> ROOT.TH1:
    """
    Convert the histogram to a density histogram.

    Parameters
    ----------
    hist : ROOT.TH1
        The histogram to be converted.
    inplace : bool
        Whether to modify the histogram in place or return a new one.
        The new one has the same name as the original one with '_density'
        appended.

    Returns
    -------
    ROOT.TH1
        The density histogram.
    """
    if not inplace:
        hist = hist.Clone()
        hist.SetName(hist.GetName() + '_density')
    hist.Scale(1/hist.Integral())
    return hist


def hist1d(
        rdf: ROOT.RDataFrame,
        x: str,
        xlow: Union[Literal['lowest'], int],
        xhigh: Union[Literal['highest'], int],
        xnbins: int,
        xlabel: str = None,
        title: str = None,
        density: bool = False) -> Tuple[str, ROOT.TH1]:
    """
    Create a 1D histogram from the RDataFrame.

    Parameters
    ----------
    rdf : ROOT.RDataFrame
        The RDataFrame to be used to create the histogram.
    x : str
        The name of the variable to be used to create the histogram.
    xlow : Union[Literal['lowest'], int]
        The lower limit of the histogram. It can be an integer or 'lowest'.
    xhigh : Union[Literal['highest'], int]
        The upper limit of the histogram. It can be an integer or 'highest'.
    xnbins : int
        The number of bins of the histogram.
    xlabel : str, optional
        The label of the x-axis, by default None
    title : str, optional
        The title of the histogram, by default None
    density : bool, optional
        Whether to create a density histogram, by default False

    Returns
    -------
    Tuple[str, ROOT.TH1]
        The histogram name and the histogram.
    """
    if xlabel is None:
        xlabel = x
    if title is None:
        title = xlabel
    hist_name = f"{x}_hist"
    hist = rdf.Histo1D(
        (hist_name,
         title,
         xnbins,
         parse_bin(xlow, rdf, x),
         parse_bin(xhigh, rdf, x)),
        x
    )
    hist.GetXaxis().SetTitle(xlabel)
    if density:
        as_density(hist, inplace=True)
        hist.GetYaxis().SetTitle("Density")
    else:
        hist.GetYaxis().SetTitle("Entries")

    return hist_name, hist


def hist2d(
        rdf: ROOT.RDataFrame,
        x: str,
        y: str,
        xlow: Union[Literal['lowest'], int],
        ylow: Union[Literal['lowest'], int],
        xhigh: Union[Literal['highest'], int],
        yhigh: Union[Literal['highest'], int],
        xnbins: int,
        ynbins: int,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        density: bool = False) -> Tuple[str, ROOT.TH2]:
    """
    Create a 2D histogram from the RDataFrame.

    Parameters
    ----------
    rdf : ROOT.RDataFrame
        The RDataFrame to be used to create the histogram.
    x : str
        The name of the x variable to be used to create the histogram.
    y : str
        The name of the y variable to be used to create the histogram.
    xlow : Union[Literal['lowest'], int]
        The lower limit of the x-axis of the histogram. It can be an integer or
        'lowest'.
    ylow : Union[Literal['lowest'], int]
        The lower limit of the y-axis of the histogram. It can be an integer or
        'lowest'.
    xhigh : Union[Literal['highest'], int]
        The upper limit of the x-axis of the histogram. It can be an integer or
        'highest'.
    yhigh : Union[Literal['highest'], int]
        The upper limit of the y-axis of the histogram. It can be an integer or
        'highest'.
    xnbins : int
        The number of bins of the x-axis of the histogram.
    ynbins : int
        The number of bins of the y-axis of the histogram.
    xlabel : str, optional
        The label of the x-axis, by default None
    ylabel : str, optional
        The label of the y-axis, by default None
    title : str, optional
        The title of the histogram, by default None
    density : bool, optional
        Whether to create a density histogram, by default False

    Returns
    -------
    Tuple[str, ROOT.TH2]
        The histogram name and the histogram.
    """
    if xlabel is None:
        xlabel = x
    if ylabel is None:
        ylabel = y
    if title is None:
        title = f"{xlabel} vs {ylabel}"
    hist_name = f"{x}_vs_{y}_hist"
    hist = rdf.Histo2D(
        (hist_name,
         title,
         xnbins,
         parse_bin(xlow, rdf, x),
         parse_bin(xhigh, rdf, x),
         ynbins,
         parse_bin(ylow, rdf, y),
         parse_bin(yhigh, rdf, y)),
        x, y
    )
    hist.GetXaxis().SetTitle(xlabel)
    hist.GetYaxis().SetTitle(ylabel)
    if density:
        as_density(hist, inplace=True)
        hist.GetZaxis().SetTitle("Density")
    else:
        hist.GetZaxis().SetTitle("Entries")

    return hist_name, hist


def make_eff_hist(data, x, xbins, chain, signal=True):
    xbins = array("d", xbins)
    splitted_chain = chain.split("_")
    et_cut = int(splitted_chain[1][1:])
    pidname = f"el_{splitted_chain[2]}"
    has_energy = data["el_et"] >= (et_cut)
    is_sample = data["target"] == 1.0 if signal else data["target"] == 0.0
    is_offline = data[pidname] if signal else ~data[pidname]
    chain_approved = data[chain]
    total_hist_samples = data.loc[has_energy & is_offline & is_sample, x]
    approved_hist_samples = data.loc[
        has_energy &
        is_offline &
        is_sample &
        chain_approved, x]

    hist_passed = ROOT.TH1F(f"{x}_{chain}_passed", "", len(xbins)-1, xbins)
    if not approved_hist_samples.empty:
        rpl.hist1d.fill(hist_passed, approved_hist_samples)

    hist_total = ROOT.TH1F(f"{x}_{chain}_total", "", len(xbins)-1, xbins)
    if not total_hist_samples.empty:
        rpl.hist1d.fill(hist_total, total_hist_samples)

    hist_eff = rpl.hist1d.divide(hist_passed, hist_total)

    return hist_eff, len(approved_hist_samples)/len(total_hist_samples)
