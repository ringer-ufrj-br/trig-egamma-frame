
MYPATH=/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_train/signal


prun_jobs.py -c "python dump_electrons.py -i %IN -o %OUT -j %JOB_ID" -i $MYPATH -o $PWD/output.root -nt 40

