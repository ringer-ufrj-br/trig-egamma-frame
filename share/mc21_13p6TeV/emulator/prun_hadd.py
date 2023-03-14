#!/usr/bin/env python3

from egamma import Slot, expand_folders
from egamma import expand_folders, Pool
import time, os
import argparse

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()



parser.add_argument('-i', '--inputs', action='store', 
    dest='input', required = False, default = None, 
    help = "The input files. Use %%IN to replace in command")

parser.add_argument('-o','--output', action='store', 
    dest='output', required = True,
    help = "The output file. Use %%OUT to replace in command")


parser.add_argument('-j', '--numberOfThreads', action='store', 
    dest='numberOfThreads', required = False, default = 2, type=int,
    help = "The number of threads.")

parser.add_argument('-f', '--nFilesPerMerge', action='store', 
    dest='nFilesPerMerge', required = False, default = 50, type=int,
    help = "The number of files per merge.")

import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

files = expand_folders(args.input, '*.root')

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


inputs = []
for l in chunks(files, args.nFilesPerMerge):
    inputs.append(' '.join(l))

command = 'hadd -f %OUT %IN'



# create pool of jobs
pool = Pool( command, args.numberOfThreads, inputs, args.output)
pool.run()
pool.merge()













