#!/usr/bin/env python3
import sys
import ROOT
import numpy as np

from trig_egamma_frame import ElectronLoop, DataframeSchemma, EventContext, GeV, ToolSvc
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame.algorithms import Filter, EventFilter, isAny_decorator, isZ_decorator, isJpsi_decorator
from trig_egamma_frame.algorithms import Efficiency, Quadrant

def main():

    print("🚀 Starting data collection test...")

    input_files = "tests/samples/run_3/*.root"
   
    acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = input_files,
                         treePath  =  "*/HLT/EgammaMon/summary/events",
                         dataframe  = DataframeSchemma.Run3,
                         outputFile = "output.root",
                         abort = True,
                      )
    from trig_egamma_frame import ToolSvc
    ToolSvc+=Filter( "Filter", [EventFilter(is_data=True, is_background=False)])


    et_bins  = [3., 7., 10., 15., 20., 30., 40., 50., 1000000.]
    eta_bins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]
    triggers = [
        "HLT_e28_lhtight_nod0_noringer_ivarloose_eEM24VHI",
    ]

    dumper = ElectronDumper('output', et_bins, eta_bins)
    for trigName in triggers:
        dumper.decorate_chain(trigName)
    dumper.decorate( "mc_isTruthElectronFromZ"          , isZ_decorator   )
    dumper.decorate( "mc_isTruthElectronFromAny"        , isAny_decorator )
    dumper.decorate( "mc_isTruthElectronFromJpsiPromt"  , isJpsi_decorator)
    is_background=False
    def is_target( ctx : EventContext ) -> np.int32:
        return np.int32(0) if is_background else np.int32(1)
    dumper.decorate( "target", is_target)

    ToolSvc+=dumper
    acc.run()
    # Dummy logic for data collection
    print("✅ Data collection successful!")
    sys.exit(0)

if __name__ == "__main__":
    main()
