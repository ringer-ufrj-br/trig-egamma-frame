from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold
from neuralnet.decorators import Summary, Reference
from tensorflow.keras.models import Model, model_from_json
import numpy as np
import os, glob,json
import tensorflow as tf
import pandas as pd
import pickle
import gzip



tag = 'v8'

tbasepath = '/home/joao.pinto/public/cern_data/tunings/Run2/Zee/v8/r1'
#tbasepath = '/home/joao.pinto/public/cern_data/tunings/Run2/Jpsi/v1/r1'
tunedname = "user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1.bkg.VProbes_EGAM7.GRL_v97.v8.25bins_et{et}_eta{eta}.r1"

#tunedname = "user.jodafons.data17-18_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM2.bkg.VProbes_EGAM7.GRL_v97.v1_et{et}_eta{eta}.r1"
outpath   = "user.jodafons.data17_13TeV.AllPeriods.sgn.probes_lhmedium_EGAM1_EGAM2.bkg.VProbes_EGAM7.GRL_v97.Run2_v8.40bins_et{et}_eta{eta}.r0"




for et in range(3,8):

    for eta in range(5):

        tpath = tbasepath+'/'+tunedname.format(et=et,eta=eta)
        print(tpath)
        for tunedpath in tqdm(glob.glob(tpath+'/*/*.npz')):
            
            ituned = dict(np.load(tunedpath, allow_pickle=True))['tunedData'][0]
            #f = gzip.GzipFile(tunedpath, 'rb')
            #o = pickle.load(f)
            #f.close()
            #ituned = o['tunedData'][0]


            # load metadata
            sort      = ituned['sort']
            init      = ituned['init']
            model_idx = ituned['imodel']
            time      = ituned['time']

            # load histoty
            history   = ituned['history']
            
            # load model
            model = model_from_json( json.dumps(ituned['sequence'], separators=(',', ':')) )
            model.set_weights( ituned['weights'] )

            # save all
            d = {
                'history' : history,
                'model'   : json.loads(model.to_json()),
                'weights' : model.get_weights(),
                'time'    : time,
                'metadata': {
                                'et_bin'  : et,
                                'eta_bin' : eta,
                                'sort'    : sort,
                                'init'    : init,
                                'model'   : model_idx,
                                'tag'     : tag,
                            }
            }

            #
            # save the model
            #
            outdir = 'job.%s.sort_%d.init_%d.model_%d' % (tag,sort, init, model_idx)
            outname = 'tuned.%s.sort_%d.init_%d.model_%d.pic' % (tag, sort, init, model_idx)
            outdir = os.getcwd()+'/'+outpath.format(et=et,eta=eta) + '/' + outdir
            os.makedirs(outdir, exist_ok=True)
            pickle.dump(d, open(outdir+'/'+outname, 'wb'))


        



