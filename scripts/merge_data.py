#!/usr/bin/env python3

from trig_egamma_frame import Slot, expand_folders
from trig_egamma_frame import expand_folders, Pool, progressbar
import time, os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()



parser.add_argument('-i', '--inputs', action='store', 
    dest='inputs', required = False, default = None, 
    help = "The input files. Use %%IN to replace in command")

parser.add_argument('-o','--output', action='store', 
    dest='output', required = True,
    help = "The output file. Use %%OUT to replace in command")





import sys,os
if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()

files = expand_folders( args.inputs )
files.sort()



for et_bin in range(8):
    for eta_bin in range(5):

        df = None
        print('et %d - eta %d'%(et_bin, eta_bin))
        for f in progressbar(files):
            if df is None:
                df = pd.read_pickle(f)
                df = df.loc[ (df.et_bin==et_bin) & (df.eta_bin==eta_bin)]
            else:
                _df = pd.read_pickle(f)
                _df = _df.loc[ (_df.et_bin==et_bin) & (_df.eta_bin==eta_bin)]
                df = pd.concat([df,_df], ignore_index=True)

        print(df.shape)




