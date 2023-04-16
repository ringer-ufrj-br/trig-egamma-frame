
import os
import json



home          = '/home/joao.pinto/public/cern_data'
ringerVersion = '/home/joao.pinto/public/cern_data/tunings/releases/Run2_20230227_v8'
model_path    = ringerVersion+'/models/data17_13TeV.EGAM1_EGAM2_probes_lhmedium.EGAM7_vetolhvloose.40bins.Electron{pidname}.Run2_v8.et{et}_eta{eta}.h5'
pidnames      = {'Tight':'tight' , 'Medium':'medium', 'Loose':'loose', 'VeryLoose':'loose'}
data          = home+'/mc21_13p6TeV/files/mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.h5'
output_name   = 'ref.et{et}_eta{eta}.json'

ref   = [[ None for _ in range(5)] for __ in range(8)]


for et_bin in range(8):

    for eta_bin in range(5):


            command = 'python dump_reference.py -i {data} --et {et} --eta {eta} -o {output} --ringerVersion {ringerVersion}'.format(
                data = data.format(et=et_bin, eta=eta_bin),
                et = et_bin,
                eta = eta_bin,
                output = output_name.format(et=et_bin, eta=eta_bin),
                ringerVersion = ringerVersion
            )

            os.system(command)
            current_ref = json.load(open(output_name.format(et=et_bin,eta=eta_bin),'r'))
            ref[et_bin][eta_bin] = current_ref


output = 'mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.ref.json'
json.dump(ref,open(output,'w'))