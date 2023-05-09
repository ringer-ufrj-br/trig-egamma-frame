#!/usr/bin/env python3
from egamma import  Pool
from egamma.core import list_files

import os
import argparse
import pandas as pd
from itertools import product

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i', '--inputs', action='store', 
    dest='inputs', required = False, default = None, nargs="+",
    help = "The input files. Use %%IN to replace in command")

parser.add_argument('-o','--output', action='store', 
    dest='output', required = True,
    help = "Output dir")

parser.add_argument('-m','--merge', action='store_true', dest='merge', 
    required = False, 
    help = "Merge all output files.")

parser.add_argument('-nt', '--numberOfThreads', action='store', 
    dest='numberOfThreads', required = False, default = 1, type=int,
    help = "The number of threads.")

parser.add_argument('-b', '--batch-size', action='store', 
    dest='batch_size', required = False, default = 1, type=int,
    help = "Number of files prossed by each job call")

parser.add_argument('-n','--nov', action='store',
    dest='nov', required = False, default = -1, type=int,
    help = "Number of events.")

parser.add_argument('-p','--path', action='store',
    dest='path', required = False, default='*/HLT/EgammaMon/summary/events', type=str,
    help = "Ntuple base path.")

parser.add_argument('-l','--level', action='store',
    dest='level', required = False, type=str, default='INFO',
    help = "VERBOSE/INFO/DEBUG/WARNING/ERROR/FATAL")

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


args = parser.parse_args()
input_files = list_files(args.inputs, "root")
input_files.sort()

command = "python dump_electrons.py"
command += " -i %IN"
command += " -o %OUT"
command += " -j %JOB_ID"
command += f" -n {args.nov}"
command += f" -p {args.path}"
command += f" -l {args.level}"
command += f" --mute"
command += f" --ringerVersion {args.ringerVersion}"
command += f" --triggers {' '.join(args.triggers)}"
command += f" --et-bins {' '.join([str(val) for val in args.et_bins])}"
command += f" --eta-bins {' '.join([str(val) for val in args.eta_bins])}"
if args.jets:
    command += " --jets"

if not os.path.exists(args.output):
    os.makedirs(args.output)
output_file = os.path.join(args.output, "dumper_output.root")
print(f"OUTPUT_FILE: {output_file}")

prun = Pool(command, args.numberOfThreads, input_files, output_file, args.batch_size)
prun.run()

# Custom merge since the electron dumper dumps the data
# into directories
if args.merge:
    _, output_dir_name = os.path.split(args.output)
    output_files = pd.Series(list_files(args.output, "root"))
    nEtBins = len(args.et_bins)-1
    nEtaBins = len(args.eta_bins)-1
    for etBinIdx, etaBinIdx in product(range(nEtBins), range(nEtaBins)):
        bin_file_end = f"_et{etBinIdx}_eta{etaBinIdx}.root"
        files2merge = output_files[output_files.str.endswith(bin_file_end)]
        joined_files2merge = ' '.join(files2merge)
        output_filename = f"{output_dir_name}{bin_file_end}.root"
        output_filepath = os.path.join(args.output, output_filename)
        hadd_command = f"hadd -f {output_filepath} {joined_files2merge}"
        os.system(hadd_command)
        rm_command = f"rm -rf {joined_files2merge}"
        os.system(rm_command)
