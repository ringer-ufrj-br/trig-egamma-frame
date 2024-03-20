"""Makes 1D Histograms from root file"""
import os
import json
import logging
import logging.config
from argparse import ArgumentParser
from egamma.root import get_tchain
from egamma.histograms import hist1d
from egamma.utils import dump_script_report, check_list_sizes
from egamma.logging import set_loggers

LOGGER_NAME = 'trig-egamma-frame-debug'


def parse_args():
    parser = ArgumentParser(
        prog=os.path.basename(__file__),
        description='Makes Histograms from root file'
    )
    parser.add_argument(
        '--filepaths', nargs='+', required=True,
        help='Files to process. Automatically opens directories'
    )
    parser.add_argument(
        '--treepath', required=True,
        help='Path to the tree inside the rootfile'
    )
    parser.add_argument(
        '--output-dir', required=True, dest='output_dir',
        help='Dir to dump the histograms'
    )
    parser.add_argument(
        '--var-names', required=True, dest='var_names',
        nargs='+',
        help='Variable names to plot'
    )
    parser.add_argument(
        '--var-labels', required=False, dest='var_labels',
        nargs='+',
        help='Variable labels to plot. If not passed, uses var_names'
    )
    parser.add_argument(
        '--titles', required=False, dest='titles',
        nargs='+',
        help='Variable titles to plot'
    )
    parser.add_argument(
        '--var-bins', required=True, dest='var_bins',
        nargs='+', type=int,
        help='Number of histogram bins'
    )
    parser.add_argument(
        '--var-lows', required=True, dest='var_lows',
        nargs='+',
        help='Histogram low limits'
    )
    parser.add_argument(
        '--var-highs', required=True, dest='var_highs',
        nargs='+',
        help='Histogram high limits'
    )
    parser.add_argument(
        '--densities', required=False, dest='densities',
        nargs='+', type=bool,
        help='True to make the hist area equal to 1'
    )
    parser.add_argument(
        '--filters', required=False, dest='filters',
        nargs='+',
        help='Filters to apply to the tree'
    )
    parser.add_argument(
        '--mt', action='store_true',
        help='If passed uses ROOT multithreading'
    )
    parser.add_argument(
        '--dev', action='store_true',
        help='If true parses only the first file found for testing'
    )

    args = parser.parse_args().__dict__
    if not args.get('densities'):
        args['densities'] = [False for _ in range(len(args['var_names']))]
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(args)

    lists2check = [
        'var_names',
        'var_labels',
        'var_bins',
        'var_lows',
        'var_highs',
        'titles',
        'densities'
    ]

    list_len = len(args['var_names'])
    if not args.get('var_labels'):
        args['var_labels'] = args['var_names']
    if not args.get('titles'):
        args['titles'] = [None for _ in range(list_len)]
    if not args.get('densities'):
        args['densities'] = [False for _ in range(list_len)]

    check_list_sizes(args, lists2check)

    if not os.path.exists(args['output_dir']):
        os.makedirs(args['output_dir'])

    with open(os.path.join(args['output_dir'], 'args.json'), 'w') as f:
        json.dump(args, f, indent=4)

    return args


def get_hist_name(var_name):
    return f'{var_name}_hist'


def main(
        filepaths,
        treepath,
        output_dir,
        var_names,
        titles,
        var_labels,
        var_bins,
        var_lows,
        var_highs,
        densities,
        filters,
        mt,
        dev) -> int:
    import os
    import ROOT
    import rootplotlib as rpl
    from tqdm import tqdm

    if mt:
        ROOT.EnableImplicitMT()

    logger = logging.getLogger(LOGGER_NAME)

    files, chain = get_tchain(filepaths, treepath, dev)
    # Hack for using eta
    # eta_field_name = 'trig_L2_calo_eta'
    # rdf = ROOT.RDataFrame(chain) \
    #     .Define(f'abs_{eta_field_name}', f'abs({eta_field_name})')
    rdf = ROOT.RDataFrame(chain)
    if filters:
        filter_str = ' && '.join(filters)
        rdf = rdf.Filter(filter_str)

    n_hists = len(var_names)

    hists = dict()
    logger.info('Building Hists')
    for i in tqdm(range(n_hists), desc='Building Hists'):
        hist_name, hist = hist1d(
            rdf,
            var_names[i],
            var_lows[i],
            var_highs[i],
            var_bins[i],
            var_labels[i],
            titles[i],
            densities[i]
        )
        hists[hist_name] = hist

    logger.info('Saving hists')
    output_file = os.path.join(output_dir, 'hists.root')
    file_op = 'recreate' if os.path.exists(output_file) else 'create'
    with ROOT.TFile(output_file, file_op):
        for hist in tqdm(hists.values(), desc='Saving Hists'):
            hist.Write()

    logger.info('Plotting hists')
    plots_dir = os.path.join(
        output_dir,
        'plots'
    )
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    for var_name, hist in hists.items():
        hist_name = get_hist_name(var_name)
        fig = rpl.create_canvas(hist_name, canw=1400, canh=1000)
        fig.add_hist(hist, drawopt='hist')
        fig.savefig(os.path.join(plots_dir, f'{hist_name}_histplot.png'))

    logger.info('Dumping report')
    dump_script_report(
        files,
        os.path.join(output_dir, 'report.txt'),
        n_samples=rdf.Count().GetValue()
    )
    return 0


if __name__ == "__main__":
    set_loggers()
    args = parse_args()
    main(**args)
