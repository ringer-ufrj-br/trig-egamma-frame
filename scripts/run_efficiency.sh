#!/bin/bash
#SBATCH --job-name=trigger
#SBATCH --partition=cpu

# Input files
# /$HOME/cern_data/mc16_13TeV/PhysVal_v2/Zee_boosted \
# $HOME/cern_data/mc21_13p6TeV/ntuple_train/signal/user.jodafons.mc21_13p6TeV.601189.PhPy8EG_AZNLO_Zee.recon.AOD.e8453_e8455_s3873_s3874_r14136.r3000_XYZ.root.tgz \
# $HOME/cern_data/mc21_13p6TeV/ntuple_test/signal/user.jodafons.mc21_13p6TeV.601189.PhPy8EG_AZNLO_Zee.recon.AOD.e8453_e8455_s3873_s3874_r14136.r3000_XYZ.root.tgz
# $HOME/cern_data/mc21_13p6TeV/ntuple_test/background/user.mverissi.mc21_13p6TeV.801278.Py8EG_A14NNPDF23LO_perf_JF17.recon.AOD.e8453_e8455_s3873_s3874_r14136.r3000_XYZ.root.tgz

# Tunings
# $HOME/cern_data/tunings/releases/Run3_20230316_v0
# $HOME/cern_data/tunings/releases/Run3_20230316_v1

# Triggers
# e140_lhloose_L1EM22VHI
# e24_lhtight_L1EM22VHI
# e60_lhmedium_L1EM22VHI

echo "I am alive"

# source $HOME/workspace/full_setup.sh

call_dir=$PWD

cd $HOME/workspace/trig-egamma-frame/scripts

# Run 3 v0 bkg
echo "-------------------------------------------------------------------------------------------------------------"
echo -e "STARTED RUN3 V0 BKG"
echo "-------------------------------------------------------------------------------------------------------------"

python run_efficiency.py \
-o $HOME/data/trigger_effs/20230418_Run3_20230316_v0_mc21_13p6TeV_Zee_test_bkg.root \
-i $HOME/cern_data/mc21_13p6TeV/ntuple_test/background/user.mverissi.mc21_13p6TeV.801278.Py8EG_A14NNPDF23LO_perf_JF17.recon.AOD.e8453_e8455_s3873_s3874_r14136.r3000_XYZ.root.tgz \
--ringerVersion $HOME/cern_data/tunings/releases/Run3_20230316_v0 \
--triggers e140_lhloose_L1EM22VHI,e24_lhtight_L1EM22VHI,e60_lhmedium_L1EM22VHI \
--cost

echo "-------------------------------------------------------------------------------------------------------------"
echo -e "FINISHED RUN3 V0 BKG"
echo "-------------------------------------------------------------------------------------------------------------"

cd $call_dir

echo "I am dead"
