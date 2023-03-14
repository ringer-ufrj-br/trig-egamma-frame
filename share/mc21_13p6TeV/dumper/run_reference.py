#!/usr/bin/env python

import traceback
import argparse
import os,sys
import pandas as pd
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
tf.config.run_functions_eagerly(False)
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.compat.v1.InteractiveSession(config=config)
tf.config.run_functions_eagerly(False)
from egamma.emulator.run3.ringer import RingerSelector
from egamma import GeV


parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-i','--inputFile', action='store',
        dest='inputFile', required = True, 
            help = "The data")
parser.add_argument('--et' , action='store',
        dest='et', required = True, default = None, type=int,
            help = "The et")
parser.add_argument('--eta' , action='store',
        dest='eta', required = True, default = None, type=int,
            help = "The eta")
parser.add_argument('-o' ,'--output', action='store',
        dest='output', required = False, default=None,
            help = "The output file")
parser.add_argument('--ringerVersion' , action='store',
        dest='ringerVersion', required = False, default='/home/joao.pinto/public/cern_data/tunings/releases/Run2_20230227_v8',
            help = "The ringer path")

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


versions = {
            "tight"     : args.ringerVersion+"/ElectronRingerTightTriggerConfig.conf",
            "medium"    : args.ringerVersion+"/ElectronRingerMediumTriggerConfig.conf",
            "loose"     : args.ringerVersion+"/ElectronRingerLooseTriggerConfig.conf",
            "vloose"    : args.ringerVersion+"/ElectronRingerVeryLooseTriggerConfig.conf",
}

hypos = {}
for pidname, path in versions.items():
    hypo = RingerSelector(ConfigPath = path)
    hypo.initialize()
    hypos[pidname] = hypo



def norm1( data ):
    norms = np.abs( data.sum(axis=1) )
    norms[norms==0] = 1
    return data/norms[:,None]

col_names= ['trig_L2_cl_ring_%d'%i for i in range(100)]

df = pd.read_hdf(args.inputFile)


def calculate(df_filted, hypo):
    eta_mean  = np.mean(abs(df_filted.trig_L2_cl_eta))
    et_mean   = df_filted.trig_L2_cl_et.mean()
    avgmu     = df_filted.avgmu.values
    col_names = ['trig_L2_cl_ring_%d'%i for i in range(100)]
    rings     = df_filted[col_names].values.astype(np.float32)
    rings     = norm1(rings)
    model     = hypo.get_model(et_mean, eta_mean).model
    cut       = hypo.get_cut(et_mean, eta_mean)
    output    = model.predict(rings, batch_size=512, verbose=1).flatten()
    avgmu[avgmu>cut.avgmumax] = cut.avgmumax
    thr = cut.slope*avgmu + cut.offset
    answer = output > thr
    total = int(answer.shape[0])
    passed = int(sum(answer))
    return passed, total


values = { pidname:{} for pidname in hypos.keys()}


for pidname , hypo in hypos.items():

    df_filted = df.loc[(df.target==1) & (df.el_lhmedium==True)]
    print(df_filted.shape)

    passed, total = calculate(df_filted, hypo)
    values[pidname]['det'] = {'total':total, 'passed':passed}
    print('et%d, eta%d , Pd = %1.4f (%s)'%(args.et,args.eta,passed/total,pidname))
 

    df_filted = df.loc[(df.target==0) & (df.el_lhvloose==False)]
    print(df_filted.shape)
    passed, total = calculate(df_filted, hypo)
    values[pidname]['fake'] = {'total':total, 'passed':passed}
    print('et%d, eta%d , Fa = %1.4f (%s)'%(args.et,args.eta,passed/total,pidname))

json.dump(values,open(args.output,'w'))