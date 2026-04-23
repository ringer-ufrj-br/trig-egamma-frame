

import sys
import json
import numpy as np
import argparse

from trig_egamma_frame import get_argparser_formatter
from trig_egamma_frame import ElectronLoop, DataframeSchemma, EventContext, GeV, ToolSvc
from trig_egamma_frame.algorithms import Filter, EventFilter, Efficiency, Quadrant




# Argument Parsing
parser = argparse.ArgumentParser(description="Example job", formatter_class=get_argparser_formatter())
parser.add_argument("--job-json", "-j", dest="job_json", type=str, default=None, help="Path to the job JSON file")
parser.add_argument("--output", "-o", dest="output", type=str, default=None, help="Path to the output file")
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

print(f"Reading job from {args.job_json}")
with open(args.job_json, 'r') as f:
    job = json.load(f)
    input_file= job["input"]
    tree_path = job["tree_path"]
    is_data = job["is_data"]
    is_background = job["is_background"]
    triggers = job["triggers"]
    quadrant_features = job["quadrant"]


acc = ElectronLoop( "ElectronLoop",
                    inputFile  = input_file,
                    treePath   = tree_path,
                    dataframe  = DataframeSchemma.Run3,
                    outputFile = args.output,
                    abort      = True,
                    )

ToolSvc+=Filter( "Filter", [EventFilter(is_data=is_data, is_background=is_background)])
ToolSvc+=Efficiency("Efficiency", triggers=triggers)

quadrant = Quadrant("Quadrant")
for feat in quadrant_features:
    quadrant.add_feature(feat[0], feat[1])

ToolSvc+=quadrant
acc.run()