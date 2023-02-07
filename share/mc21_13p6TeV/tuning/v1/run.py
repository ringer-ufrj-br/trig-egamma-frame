#!/usr/bin/env python

import traceback
import argparse
import os,sys
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-j','--job', action='store',
        dest='job', required = True, 
            help = "The job config file that will be used to configure the job (sort and init).")

parser.add_argument('-v','--volume', action='store',
        dest='volume', required = False, default=os.getcwd(),
            help = "The volume output.")

parser.add_argument('-d','--dataFile', action='store',
        dest='dataFile', required = True, default = None,
            help = "The data/target file used to train the model.")

parser.add_argument('--et', action='store',
        dest='et', required = True, default = None, type=int,
            help = "et bin")

parser.add_argument('--eta', action='store',
        dest='eta', required = True, default = None, type=int, 
            help = "eta bin")

parser.add_argument('-r' ,'--ref', action='store',
        dest='ref', required = True, default = None,
            help = "The reference file")

parser.add_argument('-o' ,'--output', action='store',
        dest='output', required = False, default = None,
            help = "The output file")

if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


#
# Data loader
#
def data_loader( path, cv, sort):

  pidname = 'el_lhmedium'
  df = pd.read_hdf(path)
  df = df.loc[ ((df[pidname]==True) & (df.target==1.0)) | ((df.target==0) & (df['el_lhvloose']==False) ) ]

  
  # for new training, we selected 1/2 of rings in each layer
  #pre-sample - 8 rings
  # EM1 - 64 rings
  # EM2 - 8 rings
  # EM3 - 8 rings
  # Had1 - 4 rings
  # Had2 - 4 rings
  # Had3 - 4 rings
  prefix = 'trig_L2_cl_ring_%i'

  # rings presmaple 
  presample = [prefix %iring for iring in range(8//2)]

  # EM1 list
  sum_rings = 8
  em1 = [prefix %iring for iring in range(sum_rings, sum_rings+(64//2))]

  # EM2 list
  sum_rings = 8+64
  em2 = [prefix %iring for iring in range(sum_rings, sum_rings+(8//2))]

  # EM3 list
  sum_rings = 8+64+8
  em3 = [prefix %iring for iring in range(sum_rings, sum_rings+(8//2))]

  # HAD1 list
  sum_rings = 8+64+8+8
  had1 = [prefix %iring for iring in range(sum_rings, sum_rings+(4//2))]

  # HAD2 list
  sum_rings = 8+64+8+8+4
  had2 = [prefix %iring for iring in range(sum_rings, sum_rings+(4//2))]

  # HAD3 list
  sum_rings = 8+64+8+8+4+4
  had3 = [prefix %iring for iring in range(sum_rings, sum_rings+(4//2))]

  col_names = presample+em1+em2+em3+had1+had2+had3
  print(col_names)

  rings = df[col_names].values.astype(np.float32)

  def norm1( data ):
      norms = np.abs( data.sum(axis=1) )
      norms[norms==0] = 1
      return data/norms[:,None]
    
  target = df['target'].values.astype(np.int16)
  rings = norm1(rings)
  splits = [(train_index, val_index) for train_index, val_index in cv.split(rings,target)]
  # return 
  return rings [ splits[sort][0]], rings [ splits[sort][1]], target [ splits[sort][0] ], target [ splits[sort][1] ]



try:
  from neuralnet import main
  main(args, data_loader)
  sys.exit(0)
except  Exception as e:
  traceback.print_exc()
  sys.exit(1)






