#!/usr/bin/env python



import argparse
import sys,os, glob
import traceback
import numpy as np
from tqdm import tqdm
import pandas as pd

parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

#
# job configuration
#

parser.add_argument('-i','--inputFiles', action='store',
    dest='inputFiles', required = True, nargs='+',
    help = "The input files.")

parser.add_argument('-o','--outputFile', action='store',
    dest='outputFile', required = False, default = None,
    help = "The output name.")

parser.add_argument('-l','--limit', action='store',
    dest='limit', required = False, default = 2000000, type=int,
    help = "Max number of events per class")
#
# event selection configuration
#



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


data = []
sgn_count = 0
bkg_count = 0
for f in tqdm(args.inputFiles, 'Merging...'):
    if not os.path.exists(f):
        continue
    try:
        df = pd.read_pickle(f)
        target = df.target.values[0]
        if target: # True (signal)
            sgn_count+=df.shape[0]
            if sgn_count > args.limit:
                continue
        else:
            bkg_count+=df.shape[0]
            if bkg_count > args.limit:
                continue
        data.append(df)
    except:
        #print('File corrupted: %s'%f)
        continue
data = pd.concat(data, ignore_index=True)
print(data.shape)
print('Signal %d , Background %d'%(sgn_count,bkg_count))
data.to_hdf(args.outputFile,key='data')



print(args.inputFiles)
