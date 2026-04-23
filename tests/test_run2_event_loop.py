#!/usr/bin/env python3
import sys
import ROOT
import numpy as np

from trig_egamma_frame import ElectronLoop, DataframeSchemma, EventContext, GeV
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame.algorithms import Filter, EventFilter, isAny_decorator, isZ_decorator, isJpsi_decorator
from trig_egamma_frame.algorithms import Efficiency, Quadrant

def main():

    print("🚀 Starting data collection test...")

    input_files = "tests/samples/run_2/*.root"
   
    acc = ElectronLoop(  "EventATLASLoop",
                         inputFile  = input_files,
                         treePath   = "*/HLT/Physval/Egamma/probes",
                         dataframe  = DataframeSchemma.Run2,
                         outputFile = "output.root",
                         abort = True,
                      )
    from trig_egamma_frame import ToolSvc
    ToolSvc+=Filter( "Filter", [EventFilter(is_data=True, is_background=False)])
    acc.run()
    # Dummy logic for data collection
    print("✅ Data collection successful!")
    sys.exit(0)

if __name__ == "__main__":
    main()
