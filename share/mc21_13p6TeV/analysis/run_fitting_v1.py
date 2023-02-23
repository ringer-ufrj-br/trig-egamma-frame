from neuralnet.analysis.crossval_table import crossval_table
from neuralnet.analysis.fit_table import fit_table
from sklearn.model_selection import StratifiedKFold
import collections
import pandas as pd
import numpy as np
import pickle
import json
import os

output_path = 'output/fitting/v1'
os.makedirs(output_path,exist_ok=True)


def load_data( path, etbin, etabin ):

    pidname = 'el_lhmedium'
    df = pd.read_hdf(path)
    df = df.loc[ ((df[pidname]==True) & (df.target==1.0)) | ((df.target==0) & (df['el_lhvloose']==False) ) ]
    
    

  
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
    
    rings = df[col_names].values.astype(np.float32)
    def norm1( data ):
        norms = np.abs( data.sum(axis=1) )
        norms[norms==0] = 1
        return data/norms[:,None]
    target = df['target'].values.astype(np.int16)
    data = norm1(rings)
    avgmu = df.avgmu.values
    return data, target, avgmu



#
# Create the reference map
#
def create_op_dict(op, decoration='reference'):
    
    d = collections.OrderedDict( {
              # validation
              "max_sp_val"      : 'summary/max_sp_val',
              "max_sp_pd_val"   : 'summary/max_sp_pd_val#0',
              "max_sp_fa_val"   : 'summary/max_sp_fa_val#0',
              # Operation
              "max_sp_op"       : 'summary/max_sp_op',
              "max_sp_pd_op"    : 'summary/max_sp_pd_op#0',
              "max_sp_fa_op"    : 'summary/max_sp_fa_op#0',
              
              # op
              'pd_ref'    : decoration+"/"+op+"/pd_ref#0",
              'fa_ref'    : decoration+"/"+op+"/fa_ref#0",
              'sp_ref'    : decoration+"/"+op+"/sp_ref",
              'pd_val'    : decoration+"/"+op+"/pd_val#0",
              'fa_val'    : decoration+"/"+op+"/fa_val#0",
              'sp_val'    : decoration+"/"+op+"/sp_val",
              'pd_op'     : decoration+"/"+op+"/pd_op#0",
              'fa_op'     : decoration+"/"+op+"/fa_op#0",
              'sp_op'     : decoration+"/"+op+"/sp_op",

              # Counts
              'pd_ref_passed'    : decoration+"/"+op+"/pd_ref#1",
              'fa_ref_passed'    : decoration+"/"+op+"/fa_ref#1",
              'pd_ref_total'     : decoration+"/"+op+"/pd_ref#2",
              'fa_ref_total'     : decoration+"/"+op+"/fa_ref#2",
              'pd_val_passed'    : decoration+"/"+op+"/pd_val#1",
              'fa_val_passed'    : decoration+"/"+op+"/fa_val#1",
              'pd_val_total'     : decoration+"/"+op+"/pd_val#2",
              'fa_val_total'     : decoration+"/"+op+"/fa_val#2",
              'pd_op_passed'     : decoration+"/"+op+"/pd_op#1",
              'fa_op_passed'     : decoration+"/"+op+"/fa_op#1",
              'pd_op_total'      : decoration+"/"+op+"/pd_op#2",
              'fa_op_total'      : decoration+"/"+op+"/fa_op#2",
    })
    return d


op_names = ['tight', 'medium', 'loose', 'vloose']

tuned_info = collections.OrderedDict({})
for op in op_names:
    tuned_info[op] = create_op_dict(op, "reference")


#
# Et/eta bins edges
# 
etbins = [3, 7, 10, 15, 20, 30, 40, 50, 1000000]
etabins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]


#
# Load all v8 Run 2 files
#
cv    = crossval_table( tuned_info, etbins = etbins, etabins = etabins )
cv.from_csv('output/crossval/table_run3_v1.csv')


et_min = 0


best_inits = cv.filter_inits("max_sp_val")
best_inits = best_inits.loc[ (best_inits.model_idx==0) & (best_inits.et_bin >= et_min)] # select all rows with 5 neurons
best_sorts = cv.filter_sorts( best_inits , 'max_sp_op')


#
# Data paths
#
datapath = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/files/mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.h5'
paths = [ [datapath.format(et=et_bin, eta=eta_bin) for eta_bin in range(5)] for et_bin in range(8)]


#
# Create references
#
ref_path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/files/data17_13TeV.AllPeriods.sgn.probes_lhvloose_EGAM1_EGAM2.bkg.vprobes_vlhvloose_EGAM7.GRL_v97.40bins.json'
refs = json.load(open(ref_path,'r'))
ref_values = [[{} for _ in range(5)] for __ in range(8)]

for et_bin in range(8):
    for eta_bin in range(5):
        for op_name in op_names:
            pd_value = refs[et_bin][eta_bin][op_name]['det']['passed']/refs[et_bin][eta_bin][op_name]['det']['total']
            fa_value = refs[et_bin][eta_bin][op_name]['fake']['passed']/refs[et_bin][eta_bin][op_name]['fake']['total']
            ref_values[et_bin][eta_bin][op_name] = {'pd':pd_value, 'fa':fa_value, 'pd_epsilon':0.0}


#
# Crossval
#
kf = StratifiedKFold(n_splits=10, random_state=512, shuffle=True)


#
# Fitting
#
fit = fit_table( etbins, etabins, kf )

#
best_sorts_refit = fit.fill( best_sorts , load_data, paths, ref_values, output_path=output_path ,
                                min_avgmu=16, max_avgmu=70, xbin_size=0.05, 
                                ybin_size=1,ymax=70)


best_sorts_refit.to_csv('output/fitting/v1/best_sorts_run3_v1.csv')
#best_sorts_refit = pd.read_csv('output/fitting/v1/best_sorts_run3_v1.csv')


for op in op_names:
    fit.dump_beamer_table( best_sorts_refit.loc[best_sorts_refit.op_name == op] ,                  
                              op+' Fitting (Run3 v1)', 'fitting_run3_v1_'+op)



#
# Export all models
#


model_name_format = 'mc21_13p6TeV.801272_Jpsie.601189_Zee.801278_perf_JF17.40bins.Electron{op}.Run3_v1.et%d_eta%d'
config_name_format = 'ElectronRinger{op}TriggerConfig.conf'
op_capnames = ['Tight', 'Medium', 'Loose', 'VeryLoose']
for idx, op in enumerate( ['tight','medium','loose','vloose'] ):
    fit.export(best_sorts_refit.loc[best_sorts_refit.op_name==op], 
                  model_name_format.format(op=op_capnames[idx]), 
                  config_name_format.format(op=op_capnames[idx]), 
                  op, 
                  to_onnx     = True,
                  remove_last = True,
                  barcode     = 1,
                  min_avgmu   = 16,
                  max_avgmu   = 100)


os.system('mv models output/fitting/v1')
os.system('mv *.conf output/fitting/v1')
os.system('mv *.pdf output/fitting/v1')
os.system('mv *.tex output/fitting/v1')