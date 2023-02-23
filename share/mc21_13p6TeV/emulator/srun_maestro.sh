#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=orchestra-executor
#SBATCH --exclusive
#SBATCH --account=joao.pinto
#SBATCH --ntasks=1

#echo $SLURM_JOB_NODELIST
#export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

DATABASE=$1
MASTER=$2

srun ./run_maestro.sh $DATABASE $MASTER
wait