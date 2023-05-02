#!/usr/bin/env python

from egamma import LoggingLevel
from egamma import ToolSvc, GeV
from egamma import ElectronLoop
from egamma.enumerators import Dataframe as DataframeEnum
from egamma.core import complete
from egamma.core import expand_folders

import glob
import argparse
import sys,os
import traceback
import numpy as np
np.random.seed(512)

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# job configuration
#

parser.add_argument('-i','--inputFile', action='store',
    dest='inputFile', required = True, nargs="+", 
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


parser.add_argument('--ringerVersion', action='store',
    dest='ringerVersion', required = True,
    help = "The ringer version")


parser.add_argument('--cost', action='store_true',
    dest='cost', required = False,
    help = "Enable this flag to switch to fake rate measurements")
    

parser.add_argument('--triggers', action='store',
    dest='triggers', required = True,
    help = "The triggers common separated")


#
# event selection configuration
#



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


try:

    inputFile = list()
    for path in args.inputFile:
        if path.endswith(".root"):
            inputFile.append(path)
        else:
            inputFile.extend(glob.glob(os.path.join(path, "**", "*.root"), recursive=True))
    
    acc = ElectronLoop(  "EventATLASLoop",
                     inputFile  = inputFile,
                     treePath   = args.path,
                     dataframe  = DataframeEnum.Run3,
                     outputFile = args.outputFile,
                     level      = getattr(LoggingLevel, args.level),
                     mute       = args.mute,
                     abort      = False,
                  )


    class MonteCarloFilter:
        def __init__ ( self, cost=False):
            self.cost=cost

        def __call__(self, ctx):

            elCont = ctx.getHandler( "ElectronContainer" )
            if elCont.et() < 2*GeV:
                return False

            fc = ctx.getHandler( "HLT__TrigEMClusterContainer" )
            if not fc.isGoodRinger():
                return False

            # Monte Carlo selection
            mc = ctx.getHandler("MonteCarloContainer")
            if self.cost:
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

    #
    # Initial filter
    #
    from egamma import Filter
    ToolSvc+=Filter( "Filter", [MonteCarloFilter(args.cost)])

    from egamma.emulator.run3 import ElectronChain as Chain
    from egamma.emulator import attach
    from egamma.emulator import electronFlags
    electronFlags.ringerVersion = args.ringerVersion


    triggers = args.triggers.split(',')
    for trigName in triggers:
        attach(Chain(trigName))

    from egamma.algorithms import Efficiency
    eff = Efficiency( "Efficiency", 
                      basepath     = 'Trigger',
                      triggers     = triggers, 
                      pidname      = '!el_lhvloose' if args.cost else None,
                    )

    ToolSvc+=eff

    acc.run(args.nov)
    sys.exit(0)

except  Exception as e:
    traceback.print_exc()
    print ('job failed')
    sys.exit(1)
