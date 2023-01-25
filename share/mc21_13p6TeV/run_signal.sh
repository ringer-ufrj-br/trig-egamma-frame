
MYPATH=/home/joao.pinto/public/cern_data/mc21_13p6TeV/ntuple_train/signal


prun_jobs.py -c "dump_electrons.py -i %IN -o %OUT" -i $MYPATH -o output.root -nt 1

