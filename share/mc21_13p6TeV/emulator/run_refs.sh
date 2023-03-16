

DEFAULT_VERSION="/home/joao.pinto/public/cern_data/tunings/releases/Run2_20230227_v8"
TRIGGERS="HLT_e5_lhvloose_L1EM3,HLT_e9_lhloose_L1EM7,HLT_e17_lhvloose_L1EM15,HLT_e26_lhtight_ivarloose_L1EM22VHI,HLT_e60_lhmedium_L1EM22VHI,HLT_e140_lhloose_L1EM22VHI"
prun_jobs.py -c "python run.py -i %IN -o %OUT --triggers $TRIGGERS --ringerVersion $DEFAULT_VERSION" -m -nt 40 -o monitoring_ref.root -i valid_samples/monitoring
prun_jobs.py -c "python run.py -i %IN -o %OUT --triggers $TRIGGERS --ringerVersion $DEFAULT_VERSION --cost" -m -nt 40 -o cost_ref.root -i valid_samples/cost


