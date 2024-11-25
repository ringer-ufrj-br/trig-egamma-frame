#!/usr/bin/env python

from egamma import LoggingLevel
from egamma import ToolSvc, GeV
from egamma import ElectronLoop
from egamma.algorithms import Inference
from egamma.enumerators import Dataframe as DataframeEnum
from egamma.core import complete

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
    dest='inputFile', required = True,
    help = "The input file.")

parser.add_argument('-t','--tunings', action='store',
    dest='tunings', required = True, type=str, nargs="+",
    help = "Path to the dir with the tunings")

parser.add_argument('-o','--outputFile', action='store',
    dest='outputFile', required = False, default = "run_inference_output.root",
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


#
# event selection configuration
#


if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()


try:

    jf17     = True if 'JF17' in args.inputFile else False

    acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = glob.glob(os.path.join(args.inputFile, '*.root')),
                         treePath   = args.path,
                         dataframe  = DataframeEnum.Run3,
                         outputFile = args.outputFile,
                         level      = getattr(LoggingLevel, 'DEBUG'),
                         mute       = args.mute,
                         abort      = False,
                      )


    class MonteCarloFilter:
        def __init__ ( self, jf17=False):
            self.jf17=jf17

        def __call__(self, ctx):

            elCont = ctx.getHandler( "ElectronContainer" )
            if elCont.et() < 2*GeV:
                return False

            fc = ctx.getHandler( "HLT__TrigEMClusterContainer" )
            if not fc.isGoodRinger():
                return False

            # Monte Carlo selection
            mc = ctx.getHandler("MonteCarloContainer")
            if self.jf17:
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


    class OfflineFilter:
        def __init__(self, pidname = '!el_lhvloose'):
            self.pidname = pidname

        def __call__(self, ctx):
            elCont = ctx.getHandler( "ElectronContainer" )
            pidname = self.pidname
            veto = True if '!' in pidname else False
            pidname = pidname.replace('!','')
            passed = False
            if veto and not elCont.accept(pidname):
                passed = True
            if not veto and elCont.accept(pidname):
                passed = True
            return passed



    #
    # Create event filters
    #
    mcFilter      = MonteCarloFilter( jf17=jf17 )
    offlineFilter = OfflineFilter( pidname='!el_lhvloose' )

    filters = [mcFilter]
    if jf17: # append offline for JF17 samples
        filters.append(offlineFilter)


    #
    # Initial filter
    #
    from egamma import Filter
    ToolSvc+=Filter( "Filter", filters)

    from egamma.emulator.run3 import RingerSelector
    home_path = os.path.expanduser("~")
    tunings_path = os.path.join(home_path, 'tunings', 'releases')
    model_list = []
    for tuning_path in args.tunings:
        _, iversion = os.path.split(tuning_path) 
        for iop in ['Tight', 'Medium', 'Loose', 'VeryLoose']:
            config_path = os.path.join(tuning_path, f'ElectronRinger{iop}TriggerConfig.conf')
            selector = RingerSelector(ConfigPath=config_path)
            model_list.append((selector, '%s_%s'%(iversion, iop)))

    val = Inference( 'Inference',
                     hypos=model_list
                   )
    ToolSvc+=val

    acc.run(args.nov)
    print('job done')
    
    complete(args.job_id)
    sys.exit(0)

except  Exception as e:
    traceback.print_exc()
    print ('job failed')
    sys.exit(1)
