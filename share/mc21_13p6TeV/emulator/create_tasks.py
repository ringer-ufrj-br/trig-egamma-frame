
import os

basepath = os.getcwd()
image = "/home/joao.pinto/public/images/root-cern_latest.sif"


def create_task( inputs, triggers, task, ringerVersion, dry_run=False, skip_test=True):

    triggers = ','.join(triggers)
    exec_cmd = 'cd /home/joao.pinto/git_repos/ringer/trig-egamma-frame \n'
    exec_cmd+= 'source setup_here.sh \n'
    exec_cmd+= 'cd %JOB_WORKAREA \n'
    exec_cmd+= f'python {basepath}/run.py -i %IN -o output.root -t {triggers} --ringerVersion {ringerVersion} --nov 1000'
        
    command = """maestro.py task create \
                -t {TASK} \
                -i {INPUTS} \
                --image {IMAGE} \
                --exec "{EXEC}" \
                """

    if dry_run:
        command += "--dry_run "

    if skip_test:
        command += "--skip_test "

    cmd     = command.format(IMAGE=image,
                             TASK=task,
                             EXEC=exec_cmd,
                             INPUTS=inputs,
                             )
    print(cmd)
    os.system(cmd)




triggers_noringer = [
                "HLT_e5_lhvloose_noringer_L1EM3",
                "HLT_e9_lhloose_noringer_L1EM7",
                "HLT_e17_lhvloose_noringer_L1EM15",
                "HLT_e26_lhtight_noringer_ivarloose_L1EM22VHI",
                "HLT_e28_lhtight_noringer_ivarloose_L1EM22VHI",
                "HLT_e60_lhmedium_noringer_L1EM22VHI",
                "HLT_e140_lhloose_noringer_L1EM22VHI",
]



triggers_default = [
                "HLT_e5_lhvloose_L1EM3",
                "HLT_e9_lhloose_L1EM7",
                "HLT_e17_lhvloose_L1EM15",
                "HLT_e26_lhtight_ivarloose_L1EM22VHI",
                "HLT_e28_lhtight_ivarloose_L1EM22VHI",
                "HLT_e60_lhmedium_L1EM22VHI",
                "HLT_e140_lhloose_L1EM22VHI",
]

triggers_ringer_v0 = [
                "HLT_e5_lhvloose_v0_L1EM3",
                "HLT_e9_lhloose_v0_L1EM7",
                "HLT_e17_lhvloose_v0_L1EM15",
                "HLT_e26_lhtight_ivarloose_v0_L1EM22VHI",
                "HLT_e28_lhtight_ivarloose_v0_L1EM22VHI",
                "HLT_e60_lhmedium_v0_L1EM22VHI",
                "HLT_e140_lhloose_v0_L1EM22VHI",
]

triggers_ringer_v1 = [
                "HLT_e5_lhvloose_v1_L1EM3",
                "HLT_e9_lhloose_v1L1EM7",
                "HLT_e17_lhvloose_v1_L1EM15",
                "HLT_e26_lhtight_ivarloose_v1_L1EM22VHI",
                "HLT_e28_lhtight_ivarloose_v1_L1EM22VHI",                
                "HLT_e60_lhmedium_v1_L1EM22VHI",
                "HLT_e140_lhloose_v1_L1EM22VHI",
]


ringerVersion    = "/home/joao.pinto/public/cern_data/tunings/releases/Run2_20230227_v8"
ringerVersion_v0 = "/home/joao.pinto/public/cern_data/tunings/releases/Run3_20230227_v0"
ringerVersion_v1 = "/home/joao.pinto/public/cern_data/tunings/releases/Run3_20230227_v1"



#
# Signal
#

task = 'user.jodafons.mc21_13p6TeV.601180_Zee.801272_Jpsie3e3.sample_test.efficiency.noringer.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/signal'
#create_task(path, triggers_noringer, task, ringerVersion)

task = 'user.jodafons.mc21_13p6TeV.601180_Zee.801272_Jpsie3e3.sample_test.efficiency.ringer_Run2_v8.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/signal'
#create_task(path, triggers_default, task, ringerVersion)


task = 'user.jodafons.mc21_13p6TeV.601180_Zee.801272_Jpsie3e3.sample_test.efficiency.ringer_Run3_v0.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/signal'
#create_task(path, triggers_ringer_v0, task, ringerVersion_v0)


task = 'user.jodafons.mc21_13p6TeV.601180_Zee.801272_Jpsie3e3.sample_test.efficiency.ringer_Run3_v1.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/signal'
#create_task(path, triggers_ringer_v1, task, ringerVersion_v1)



#
# Background
#

task = 'user.jodafons.mc21_13p6TeV.mc21_13p6TeV.801278_perf_JF17.sample_test.efficiency.noringer.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/background'
create_task(path, triggers_noringer, task, ringerVersion)

task = 'user.jodafons.mc21_13p6TeV.mc21_13p6TeV.801278_perf_JF17.sample_test.efficiency.ringer_Run2_v8.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/background'
create_task(path, triggers_default, task, ringerVersion)

task = 'user.jodafons.mc21_13p6TeV.mc21_13p6TeV.801278_perf_JF17.sample_test.efficiency.ringer_Run3_v0.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/background'
create_task(path, triggers_ringer_v0, task, ringerVersion_v0)

task = 'user.jodafons.mc21_13p6TeV.mc21_13p6TeV.801278_perf_JF17.sample_test.efficiency.ringer_Run3_v1.r1'
path = '/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_test/background'
create_task(path, triggers_ringer_v1, task, ringerVersion_v1)
