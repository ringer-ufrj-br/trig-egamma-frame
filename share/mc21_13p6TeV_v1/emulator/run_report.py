


import numpy as np
import pandas as pd
import collections
import os, sys, argparse
import rootplotlib as rpl
from pprint import pprint
from copy import deepcopy
import gc
from pybeamer import *

from ROOT import kBlack,kBlue,kRed,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow,kWhite,TColor,gStyle
rpl.set_atlas_style()

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# job configuration
#

parser.add_argument('-r','--ref', action='store',
    dest='ref', required = True,
    help = "The reference file.")

parser.add_argument('-rn','--ref-name', action='store',
    dest='ref_name', default="Ref",
    help = "The reference file model name.")

parser.add_argument('-t','--test', action='store',
    dest='test', required = False, default = None,
    help = "The test file")

parser.add_argument('-tn','--test-name', action='store',
    dest='test_name', default="Test",
    help = "The test file model name")

parser.add_argument('-d','--dirname', action='store',
    dest='dirname', required = False, default='report', type=str,
    help = "directory output name")

parser.add_argument('-l','--label', action='store',
    dest='label', required = False, type=str, default='Internal, pp MC21 #sqrt{s}= 13p6TeV',
    help = "extra label")

parser.add_argument('-o','--output', action='store',
    dest='output', required = False, default='trigger_report.pdf', 
    help = "The PDF output name")

parser.add_argument('-rt','--report-title', action='store',
    dest='report_title', required = False, default="Trigger Report", 
    help = "The PDF report title")

parser.add_argument('-p','--do_plots', action='store_true',
    dest='do_plots', required = False,
    help = "Do plots")

parser.add_argument("-b", "--bkg", action="store_true")

parser.add_argument("-c", "--chain-type", action="store",
                   dest="chain_type", type=str,
                   choices=["e", "g"],
                   help='IF "e" reports on electron chain, if "g" reports on phton chain')

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()



class Reader:
    def __init__(self, path, basepath = '/Trigger'):
        self.basepath = basepath
        from egamma.core import restoreStoreGate
        self.store = restoreStoreGate(path)
        dirs = self.store.getDirs()
        self.trigger = np.unique([ dir.split('/')[2] for dir in dirs]).tolist()
        
    def profile(self, trigger, step, var):
        numerator = self.histogram(trigger, step, 'match_'+var)
        denominator = self.histogram(trigger, step, var)
        return rpl.hist1d.divide(numerator,denominator)

    def histogram(self,trigger, step, var):
        return self.store.histogram(self.basepath+'/'+trigger+'/Efficiency/'+step+'/'+var)


def plot_eff(reader_ref, reader, trigger, step, var, label_var, basepath, legends = ['Ref', 'New'], label='Internal, pp MC21 #sqrt{s}= 13p6TeV',
             is_bkg=False):

    colors = [kBlack,kBlue-4]
    markers = [23, 24]
    hists = [reader_ref.profile(trigger, step, var),
             reader_test.profile(trigger, step, var)]
    
    def add_legend(x, y, legends, pad=None):
        rpl.add_legend( legends,x,y,x+0.98,y+0.20,textsize=18, option='p', pad=pad)
    
    fig = rpl.plot_profiles(hists=hists,
                            xlabel=label_var,
                            ylabel="Trigger Efficiency",
                            ratio_label="Test/Ref",
                            colors=colors,
                            markers=markers,
                            doRatioCanvas=True)
    rpl.set_atlas_label(0.2,0.88,label)
    add_legend( 0.75,0.78, legends, pad="pad_top")
    rpl.add_text( 0.2, 0.8, trigger, textsize=0.04)

    ymin_top, ymax_top = rpl.get_yaxis_ranges(pad="pad_top")
    if is_bkg:
        fig.set_yaxis_ranges(ymin, ymax_top*1.3, "pad_top")
    else:
        if abs(ymin_top - ymax_top) > 0.4:
            ymax_top = 1.5
        else:
            ymax_top = 1.02
        fig.set_yaxis_ranges(ymin_top, ymax_top, "pad_top")
    
    ymin_bot, ymax_bot = rpl.get_yaxis_ranges(pad="pad_bot")
    fig.set_yaxis_ranges(0.7*ymin_bot, 1.3*ymax_bot, "pad_bot")

    figure_path = basepath + '/' + trigger + '_' + step + '_' + var + '.pdf'
    fig.savefig(figure_path)
    return figure_path     


def get_counts( reader , trigger, step ):
    num = reader.histogram(trigger, step, 'match_eta').GetEntries()
    den = reader.histogram(trigger, step, 'eta').GetEntries()
    return num, den, num/den

#
# Open all files
#

reader_ref  = Reader(args.ref)
reader_test = Reader(args.test)

# Create folder
os.makedirs(args.dirname, exist_ok=True)


#
# Make all plots
#

triggers = reader_ref.trigger
print(triggers)


var_names = ['et', 'highet','eta', 'mu']
var_labels = {
    'et'    : 'Offline isolated electron E_{T} [GeV]',
    'highet'    : 'Offline isolated electron E_{T} [GeV]',
    'eta'   : '#eta',
    'phi'   : '#phi',
    'mu'    : '<#mu>',
}


# Slide maker
with BeamerTexReportTemplate1( theme = 'Berlin'
                             , _toPDF = True
                             , title = args.report_title
                             , outputFile = args.output
                             , font = 'structurebold' ):
           

    for trigger in triggers:
            
            if args.chain_type == "e":
                steps = ['L1Calo', 'FastCalo','FastElectron','PrecisionCalo', 'PrecisionElectron']
            else:
                steps = ['L1Calo', 'FastCalo','FastPhoton','PrecisionCalo', 'PrecisionPhoton']

            if args.do_plots:
                for step in steps:
                    legends = [args.ref_name, args.test_name]
                    figures = [ plot_eff(reader_ref, reader_test, trigger, step, var, var_labels[var], args.dirname, legends = legends, label=args.label,
                                        is_bkg=args.bkg) for var in var_names ]
                    BeamerMultiFigureSlide( title = trigger.replace('_','\_') + ' (' +step+ ')'
                    , paths = figures
                    , nDivWidth = 2 # x
                    , nDivHeight = 2 # y
                    , texts=None
                    , fortran = False
                    )
            
            lines = []
            lines += [ HLine(_contextManaged = False) ]
            lines += [ HLine(_contextManaged = False) ]
            lines += [ TableLine( columns = ['step','Ref. [\%]','Test [\%]', 'Diff [\%]'], _contextManaged = False ) ]
            lines += [ HLine(_contextManaged = False) ]
            
            for step in steps:
                den, num, eff_ref = get_counts(reader_ref, trigger, step)
                values = [step, '%1.2f (%d/%d)'%(eff_ref*100, den, num)]
                den, num, eff_test = get_counts(reader_test, trigger, step)
                values.extend(['%1.2f (%d/%d)'%(eff_test*100, den, num)])
                values.append( '%1.2f'%(abs(eff_ref-eff_test)*100))
                lines += [ TableLine( columns = values   , _contextManaged = False ) ]
                lines += [ HLine(_contextManaged = False) ]
            lines += [ HLine(_contextManaged = False) ]

            with BeamerSlide( title = trigger.replace('_','\_')  ):
                with Table( caption = 'The general efficiency for each trigger step.') as table:
                     with ResizeBox( size = 0.7 ) as rb:
                        with Tabular( columns = 'lc' + 'c' * 3 ) as tabular:
                            tabular = tabular
                            for line in lines:
                                if isinstance(line, TableLine):
                                    tabular += line
                                else:
                                    TableLine(line, rounding = None)




