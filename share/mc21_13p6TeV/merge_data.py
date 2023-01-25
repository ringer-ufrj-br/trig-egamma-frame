#!/usr/bin/env python3

from egamma import Slot, expand_folders
from egamma import expand_folders, Pool, progressbar
from tqdm import tqdm
import time, os
import argparse
import pandas as pd
import sys,os,re



output = 'mc21_13p6TeV.80127X.P8B_A14_CTEQ6L1_Jpsie.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et%d_eta%d.h5'
#output2 = 'mc21_13p6TeV.601189.PhPy8EG_AZNLO_Zee.Py8EG_A14NNPDF23LO_perf_JF17.40bins'

limit     = 2000000 # 2M events


files = expand_folders( 'mc21_data' )


for et_bin in range(3):
    for eta_bin in range(5):
        key = f'et{et_bin}_eta{eta_bin}'
        data = []
        sgn_count = 0
        bkg_count = 0
        for file in tqdm(files, 'Merging (et=%d,eta=%d)'%(et_bin, eta_bin)):
            if not key in file:
                continue
            try:
                df = pd.read_pickle(file)
                target = df.target.values[0]
                if target: # True (signal)
                    sgn_count+=df.shape[0]
                    if sgn_count > limit:
                        continue
                else:
                    bkg_count+=df.shape[0]
                    if bkg_count > limit:
                        continue
                data.append(df)
            except:
                print('File corrupted: %s'%file)
                continue
        data = pd.concat(data, ignore_index=True)
        print(data.shape)
        print('Signal %d , Background %d'%(sgn_count,bkg_count))
        data.to_hdf(output%(et_bin,eta_bin),key='data')



