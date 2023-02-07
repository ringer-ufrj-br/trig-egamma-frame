import os
basepath = os.getcwd()

ref = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/files/data17_13TeV.AllPeriods.sgn.probes_lhvloose_EGAM1_EGAM2.bkg.vprobes_vlhvloose_EGAM7.GRL_v97.40bins.json'
image = "/home/joao.pinto/public/images/neuralnet_latest.sif"


for et in range(8):
  for eta in range(5):

    data     = f'/home/joao.pinto/public/cern_data/mc21_13p6TeV/files/mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.h5'
    exec_cmd = f'python {basepath}/run.py -j %IN --et {et} --eta {eta} -r {ref} -d {data}'
    task     = f'mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.v1'

    command = """maestro.py task create \
      -t {TASK} \
      -i {PATH}/jobs \
      --image {IMAGE} \
      --exec "{EXEC}" \
      --skip_test
      """
    cmd = command.format(PATH=basepath,EXEC=exec_cmd,IMAGE=image,TASK=task)
    print(cmd)
    os.system(cmd)

 

