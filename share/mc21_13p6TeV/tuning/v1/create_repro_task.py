
import os

basepath = os.getcwd()


image = "/home/joao.pinto/public/images/neuralnet_latest.sif"
home  = '/home/joao.pinto/public/cern_data'

for et in range(8):

    for eta in range(5):

        ref    = home+'/mc21_13p6TeV/files/data17_13TeV.AllPeriods.sgn.probes_lhvloose_EGAM1_EGAM2.bkg.vprobes_vlhvloose_EGAM7.GRL_v97.40bins.json'
        data   = home+f'/mc21_13p6TeV/files/mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.h5'
        inputs = home+f'/tunings/Run3/mc21_13p6TeV/v1/r0/mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et{et}_eta{eta}.v1'
        task   = f'user.jodafons.mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.Run3_v1.40bins_et{et}_eta{eta}.r1'


        exec_cmd = 'cd /home/joao.pinto/git_repos/ringer/neuralnet \n'
        exec_cmd+= 'source dev_envs.sh \n'
        exec_cmd+= 'cd %JOB_WORKAREA \n'
        exec_cmd+= f'python {basepath}/run_repro.py -i %IN -d {data} -r {ref}'

        command = """maestro.py task create \
                    -t {TASK} \
                    -i {INPUTS} \
                    --image {IMAGE} \
                    --exec "{EXEC}" \
                    --skip_test \
                    """

        cmd     = command.format(IMAGE=image,
                                 TASK=task,
                                 EXEC=exec_cmd,
                                 INPUTS=inputs,
                                 )

        print(cmd)
        os.system(cmd)





