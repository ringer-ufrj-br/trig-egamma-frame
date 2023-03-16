

import collections
from neuralnet.analysis.crossval_table import crossval_table
import pandas as pd
import os


output_path = 'output/crossval'
os.makedirs(output_path,exist_ok=True)




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
cv_v0    = crossval_table( tuned_info, etbins = etbins, etabins = etabins )
cv_v1    = crossval_table( tuned_info, etbins = etbins, etabins = etabins )


cv_v0.fill( '/home/joao.pinto/public/cern_data/tunings/Run3/v0/r1/user.jodafons.mc21_13p6TeV*/*/*.pic', 'Run3-v0')
cv_v1.fill( '/home/joao.pinto/public/cern_data/tunings/Run3/v1/r1/user.jodafons.mc21_13p6TeV*/*/*.pic', 'Run3-v1')

cv_v0.to_csv(output_path+'/table_run3_v0.csv')
cv_v1.to_csv(output_path+'/table_run3_v1.csv')



cv_v0.from_csv(output_path+'/table_run3_v0.csv')
cv_v1.from_csv(output_path+'/table_run3_v1.csv')




best_inits_v0 = cv_v0.filter_inits("max_sp_val")
best_inits_v0 = best_inits_v0.loc[ (best_inits_v0.model_idx==0) & (best_inits_v0.et_bin >= 3)] # select all rows with 5 neurons
best_sorts_v0 = cv_v0.filter_sorts( best_inits_v0 , 'max_sp_op')

best_inits_v1 = cv_v1.filter_inits("max_sp_val")
best_inits_v1 = best_inits_v1.loc[(best_inits_v1.model_idx==0) & (best_inits_v1.et_bin >= 3)]
best_sorts_v1 = cv_v1.filter_sorts( best_inits_v1 , 'max_sp_op')





best_inits = pd.concat([
                        best_inits_v0,
                        best_inits_v1,
            
                       ])
best_sorts = pd.concat([
                        best_sorts_v0,
                        best_sorts_v1,
                       ])



for op in op_names:
    cv_v1.dump_beamer_table( best_inits.loc[best_inits.op_name == op] ,  
                            'tuning_run3_Zee_'+op, 
                             title = op+' Tunings Zee', 
                             tags = ['Run3-v0', 'Run3-v1']
                           )




best_inits_v0 = cv_v0.filter_inits("max_sp_val")
best_inits_v0 = best_inits_v0.loc[ (best_inits_v0.model_idx==0) & (best_inits_v0.et_bin < 3)] # select all rows with 5 neurons
best_sorts_v0 = cv_v0.filter_sorts( best_inits_v0 , 'max_sp_op')

best_inits_v1 = cv_v1.filter_inits("max_sp_val")
best_inits_v1 = best_inits_v1.loc[(best_inits_v1.model_idx==0) & (best_inits_v1.et_bin < 3)]
best_sorts_v1 = cv_v1.filter_sorts( best_inits_v1 , 'max_sp_op')



best_inits = pd.concat([
                        best_inits_v0,
                        best_inits_v1,
            
                       ])
best_sorts = pd.concat([
                        best_sorts_v0,
                        best_sorts_v1,
                       ])


for op in op_names:
    cv_v1.dump_beamer_table( best_inits.loc[best_inits.op_name == op] ,  
                            'tuning_run3_Jpsi_'+op, 
                             title = op+' Tunings Jpsi', 
                             tags = ['Run3-v0', 'Run3-v1']
                           )


os.system('mv *.pdf output/crossval')
os.system('mv *.tex output/crossval')

