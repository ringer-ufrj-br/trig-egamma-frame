

import numpy as np

from trig_egamma_frame import ElectronLoop, DataframeSchemma, EventContext, GeV, ToolSvc
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame.algorithms import Filter, EventFilter, isAny_decorator, isZ_decorator, isJpsi_decorator
from trig_egamma_frame.algorithms import Efficiency, Quadrant


is_jets = False


my_filter = EventFilter(is_data=True, is_background=is_jets)
#input_files = "/mnt/shared/storage03/projects/cern/data/data17_13TeV/PhysVal_v2/EGAM1/after_ts1"

input_files = "/mnt/shared/storage03/projects/cern/data/mc21_13p6TeV/no_restrictions/user.isilvafe.mc21_13p6TeV.Zee.AOD.r14136_2sigma_constraint_26.10.23_v0_EXT0.tap_zee_5M_XYZ.root.tgz/*.root"
output = 'test'
et_bins  = [3., 7., 10., 15., 20., 30., 40., 50., 1000000.]
eta_bins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]
triggers = [
   "HLT_e28_lhtight_nod0_noringer_ivarloose_eEM24VHI",
   "HLT_e28_lhtight_nod0_ringer_v1_ivarloose_eEM24VHI",
]



acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = input_files,
                         #treePath   = "*/HLT/Physval/Egamma/probes",
                         treePath  =  "*/HLT/EgammaMon/summary/events",
                         dataframe  = DataframeSchemma.Run3,
                         outputFile = "output.root",
                         abort = True,
                      )



ToolSvc+=Filter( "Filter", [my_filter])
#dumper = ElectronDumper(output, et_bins, eta_bins)
#for trigName in triggers:
#    dumper.decorate_chain(trigName)
#dumper.decorate( "mc_isTruthElectronFromZ"          , isZ_decorator   )
#dumper.decorate( "mc_isTruthElectronFromAny"        , isAny_decorator )
#dumper.decorate( "mc_isTruthElectronFromJpsiPromt"  , isJpsi_decorator)
#is_background=False
#def is_target( ctx : EventContext ) -> np.int32:
#    return np.int32(0) if is_background else np.int32(1)
#dumper.decorate( "target", is_target)
#ToolSvc+=dumper


ToolSvc+=Efficiency("Efficiency", triggers=triggers)


quadrant = Quadrant("Quadrant")

quadrant.add_feature(
    "HLT_e28_lhtight_nod0_noringer_ivarloose_eEM24VHI",
    "HLT_e28_lhtight_nod0_ringer_v1_ivarloose_eEM24VHI"
)


ToolSvc+=quadrant
acc.run(10000)