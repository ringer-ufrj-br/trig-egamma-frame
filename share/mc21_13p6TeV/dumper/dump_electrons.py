#!/usr/bin/env python

from egamma import LoggingLevel
from egamma import ToolSvc, GeV
from egamma import ElectronLoop
from egamma.enumerators import Dataframe as DataframeEnum
from egamma.core import complete

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
#
# event selection configuration
#



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


try:

    et_bins = [4.0,7.0,10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 13000]
    eta_bins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]


    acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = args.inputFile,
                         treePath   = args.path,
                         dataframe  = DataframeEnum.Run3,
                         outputFile = args.outputFile,
                         level      = getattr(LoggingLevel, args.level),
                         mute       = args.mute,
                         abort      = False,
                      )


    class MyFilter:
        def __init__ ( self, background=False):
            self.background=background

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
            if self.background:
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


    background = True if 'JF17' in args.inputFile else False
    my_filter = MyFilter(background)


    #
    # Initial filter
    #

    from egamma import Filter
    filter = Filter( "Filter", [my_filter])
    ToolSvc+=filter


    #
    # Electron dumper
    #
    from egamma.dumper import ElectronDumper_v2 as ElectronDumper


    output = args.inputFile.split('/')[-1].replace('.root','')

    dumper = ElectronDumper(output, et_bins, eta_bins )



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
        # get the target value from the sample
        return 0 if background else 1 # signal (Zee or Jpsiee)


    dumper.decorate( "mc_isTruthElectronFromZ"          , isZ_decorator   )
    dumper.decorate( "mc_isTruthElectronFromAny"        , isAny_decorator )
    dumper.decorate( "mc_isTruthElectronFromJpsiPromt"  , isJpsi_decorator)
    dumper.decorate( "target", target)


    ToolSvc+=dumper
    acc.run(args.nov)
    print('job done')
    os.system('rm %s'%args.outputFile)
    complete(args.job_id)
    sys.exit(0)

except  Exception as e:
    traceback.print_exc()
    print ('job failed')
    sys.exit(1)
