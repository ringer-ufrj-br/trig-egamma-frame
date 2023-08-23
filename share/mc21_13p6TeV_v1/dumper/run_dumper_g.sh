
MYPATH=/data/atlas/lbalabra/test_juan/run/sample_mc23_big.root
TTREEPATH=\run_410000/summary/events
prun_jobs.py -c "python dump_photons.py -i %IN -o %OUT -j %JOB_ID -p $TTREEPATH" -i $MYPATH -o $PWD/output.root -nt 100

