#!/usr/bin/env python

from egamma import LoggingLevel
from egamma import ToolSvc, GeV
from egamma import ElectronLoop
from egamma.enumerators import Dataframe as DataframeEnum
from egamma.core import complete
from egamma.core import list_files

import argparse
import sys,os
import traceback
import numpy as np
np.random.seed(512)


class MyFilter:
    def __init__ ( self, jets=False):
        self.jets=jets

    def __call__(self, ctx):

        elCont = ctx.getHandler( "ElectronContainer" )
        if elCont.et() < 2*GeV:
            return False

        fc = ctx.getHandler( "HLT__TrigEMClusterContainer" )
        if not fc.isGoodRinger():
            return False

        #
        # Monte Carlo selection
        #
        mc = ctx.getHandler("MonteCarloContainer")
        if self.jets:
            if mc.isTruthElectronFromAny():
                return False
        else:
            if fc.et() < 15*GeV: # Jpsiee
                if not mc.isTruthElectronFromJpsiPrompt():
                    return False
            else: # Zee
                if not mc.isTruthElectronFromZ():
                    return False
        return True


parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# job configuration
#

parser.add_argument('-i','--inputFile', action='store',
    dest='inputFile', required = True, nargs='+',
    help = "The input file.")

parser.add_argument('-o','--outputFile', action='store',
    dest='outputFile', required = False, default = None,
    help = "The output name.")

parser.add_argument('-n','--nov', action='store',
    dest='nov', required = False, default = -1, type=int,
    help = "Number of events.")

parser.add_argument('-p','--path', action='store',
    dest='path', required = False, default='*/HLT/EgammaMon/summary/events', type=str,
    help = "Ntuple base path.")

parser.add_argument('-l','--level', action='store',
    dest='level', required = False, type=str, default='INFO',
    help = "VERBOSE/INFO/DEBUG/WARNING/ERROR/FATAL")

parser.add_argument('--mute', action='store_true',
    dest='mute', required = False, 
    help = "Use this for production. quite output")

parser.add_argument('-j','--job_id', action='store',
    dest='job_id', required = False, default=0, type=int,
    help = "The job id for parallel processing.")

parser.add_argument('--ringerVersion', action='store',
    dest='ringerVersion', required = False,
    help = "The ringer version")

parser.add_argument("--triggers", action="store",
    nargs="+", required=False, default=[],
    help="Triggers to be included")

parser.add_argument("--jets", action="store_true",
                    help="If passed considers the input data as jets")

parser.add_argument("--et-bins", type=float, dest="et_bins",
                    help="Et bins edges sorted", nargs="+",
                    default=[3., 7., 10., 15., 20., 30., 40., 50., 1000000.])

parser.add_argument("--eta-bins", type=float, dest="eta_bins",
                    help="Eta bins edges sorted", nargs="+",
                    default=[0.0, 0.8, 1.37, 1.54, 2.37, 2.50])

#
# event selection configuration
#

args = parser.parse_args()
input_files = list_files(args.inputFile, "root")

try:
    acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = input_files,
                         treePath   = args.path,
                         dataframe  = DataframeEnum.Run3,
                         outputFile = args.outputFile,
                         level      = getattr(LoggingLevel, args.level),
                         mute       = args.mute,
                         abort      = False,
                      )

    my_filter = MyFilter(args.jets)

    #
    # Initial filter
    #
    from egamma.emulator import electronFlags
    electronFlags.ringerVersion = args.ringerVersion
    
    from egamma import Filter
    ToolSvc+=Filter( "Filter", [my_filter])

    #
    # Electron dumper
    #
    from egamma.dumper import ElectronDumper_v2 as ElectronDumper
    dumper_output = args.outputFile.replace('.root', '')
    dumper = ElectronDumper(dumper_output, args.et_bins, args.eta_bins)

    def isZ_decorator( ctx ):
        mc = ctx.getHandler("MonteCarloContainer")
        return mc.isTruthElectronFromZ()
    def isAny_decorator( ctx ):
        mc = ctx.getHandler("MonteCarloContainer")
        return mc.isTruthElectronFromAny()
    def isJpsi_decorator( ctx ):
        mc = ctx.getHandler("MonteCarloContainer")
        return mc.isTruthElectronFromJpsiPrompt()
    def target( ctx ):
        return 0 if args.jets else 1
    
    for trigName in args.triggers:
        dumper.decorate_chain(trigName)
    dumper.decorate( "mc_isTruthElectronFromZ"          , isZ_decorator   )
    dumper.decorate( "mc_isTruthElectronFromAny"        , isAny_decorator )
    dumper.decorate( "mc_isTruthElectronFromJpsiPromt"  , isJpsi_decorator)
    dumper.decorate( "target", target)

    ToolSvc+=dumper
    acc.run(args.nov)
    os.system('rm %s'%args.outputFile)
    # complete(args.job_id)
    sys.exit(0)

except  Exception as e:
    traceback.print_exc()
    print ('job failed')
    sys.exit(1)
