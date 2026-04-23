

import os, json
from pprint import pprint
from maestro_lightning import Flow, Task, Dataset, Image
from expand_folders import expand_folders

basepath     = os.getcwd()
cern_data    = os.environ["CERN_DATA"]
dataset_path = f"{cern_data}/mc21_13p6TeV/no_restrictions/user.isilvafe.mc21_13p6TeV.Zee.AOD.r14136_2sigma_constraint_26.10.23_v0_EXT0.tap_zee_5M_XYZ.root.tgz"
input_path   = f"{basepath}/jobs"

triggers = [
   "HLT_e28_lhtight_nod0_noringer_ivarloose_eEM24VHI",
   "HLT_e28_lhtight_nod0_ringer_v1_ivarloose_eEM24VHI",
]

envs = {
    "CERN_DATA": cern_data
}

os.makedirs(input_path, exist_ok=True)

paths = expand_folders(dataset_path)

for i,path in enumerate(paths):

    with open(f"{input_path}/job_{i}.json",'w') as f:
        d={
            "input"         : path,
            "output"        : f"output.root",
            "tree_path"     : "*/HLT/EgammaMon/summary/events",
            "is_data"       : False,
            "is_background" : False,
            "triggers"      : triggers,
            "quadrant"      : [(triggers[0],triggers[1])]
        }
        json.dump(d,f)

envname = os.environ["ENV_NAME"]

with Flow(name="task", 
          path=f"{basepath}/task", 
          condaenv=envname, 
          partition="cpu") as session:

    input_dataset   = Dataset(name="jobs", path=f"{basepath}/jobs")
    pre_exec = f"echo 'do some pre-exec here...'"
    command = f"{pre_exec} && python {basepath}/job.py -j %IN -o %OUT"
    binds = {
        "/mnt/shared/storage03/projects/cern/data": "/mnt/shared/storage03/projects/cern/data",
    }
    task_1 = Task(name="task",
                  command=command,
                  input_data=input_dataset,
                  outputs={'OUT':'output.root'},
                  partition='cpu',
                  binds=binds,
                  envs=envs)

    session.run()

    

    
