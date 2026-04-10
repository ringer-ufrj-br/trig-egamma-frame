

import numpy as np

from trig_egamma_frame import ElectronLoop, DataframeSchemma, EventContext, GeV
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame import Filter
from trig_egamma_frame.kernel import ToolSvc



class MyFilter:
    def __init__ ( self, jets : bool=False):
        self.jets=jets

    def __call__(self, ctx : EventContext) -> bool:

        elCont = ctx.getHandler( "ElectronContainer" )
        if elCont.et() < 2*GeV:
            return False
        fc = ctx.getHandler( "HLT__TrigEMClusterContainer" )
        if not fc.isGoodRinger():
            return False
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

def isZ_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromZ())
def isAny_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromAny())
def isJpsi_decorator( ctx : EventContext ) -> np.int32:
    mc = ctx.getHandler("MonteCarloContainer")
    return np.int32(mc.isTruthElectronFromJpsiPrompt())
def target( ctx : EventContext ) -> np.int32:
    return np.int32(0) if args.jets else np.int32(1)
    

my_filter = MyFilter()
input_files = "/mnt/shared/storage03/projects/cern/data/data17_13TeV/PhysVal_v2/EGAM1/after_ts1"
output = 'test'
et_bins  = [3., 7., 10., 15., 20., 30., 40., 50., 1000000.]
eta_bins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]
triggers = [
   "HLT_e28_lhtight_nod0_ivarloose"
]



acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = input_files,
                         treePath   = "*/HLT/Physval/Egamma/probes",
                         dataframe  = DataframeSchemma.Run2,
                         outputFile = "output.root",
                      )



ToolSvc+=Filter( "Filter", [my_filter])



dumper = ElectronDumper(output, et_bins, eta_bins)


for trigName in triggers:
    dumper.decorate_chain(trigName)

dumper.decorate( "mc_isTruthElectronFromZ"          , isZ_decorator   )
dumper.decorate( "mc_isTruthElectronFromAny"        , isAny_decorator )
dumper.decorate( "mc_isTruthElectronFromJpsiPromt"  , isJpsi_decorator)
dumper.decorate( "target", target)

ToolSvc+=dumper

acc.run(1000)