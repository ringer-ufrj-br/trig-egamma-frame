import os

image = "/home/joao.pinto/public/images/root-cern_latest.sif"
repo = "/home/joao.pinto/git_repos/ringer/trig-egamma-frame"

exec_cmd = f"cd {repo} \n"
exec_cmd+= f"source /setup_envs.sh \n"
exec_cmd+= f"source setup_here.sh \n"
exec_cmd+= f"cd %JOB_WORKAREA \n"
exec_cmd+= f"dump_electrons.py -i %IN -o %JOB_NAME.pic --mute\n"
#exec_cmd+= f"rm *.sh \n"




command = """maestro.py task create \
  -t mc21_data \
  -i /home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple/train \
  --image {IMAGE} \
  --exec "{EXEC}" \
  """
  
cmd = command.format(EXEC=exec_cmd,IMAGE=image)
print(cmd)
os.system(cmd)


