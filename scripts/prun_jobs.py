#!/usr/bin/env python3

from egamma import Slot, expand_folders
from egamma import expand_folders, Pool
import time, os
import argparse

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()



parser.add_argument('-i', '--inputs', action='store', 
    dest='inputs', required = False, default = None, 
    help = "The input files. Use %%IN to replace in command")

parser.add_argument('-o','--output', action='store', 
    dest='output', required = True,
    help = "The output file. Use %%OUT to replace in command")

parser.add_argument('-c','--command', action='store', 
    dest='command', required = True,
    help = "The command")

parser.add_argument('-m','--merge', action='store_true', dest='merge', 
                    required = False, 
                    help = "Merge all output files.")

parser.add_argument('-nt', '--numberOfThreads', action='store', 
    dest='numberOfThreads', required = False, default = 1, type=int,
    help = "The number of threads.")


import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

files = expand_folders( args.inputs )
files.sort()
prun = Pool( args.command, args.numberOfThreads, files, args.output)
prun.run()
if args.merge:
  prun.merge()
