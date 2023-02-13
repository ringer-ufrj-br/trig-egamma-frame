
RESERVATION=joao.pinto_10
DATABASE=ringer

sbatch --reservation $RESERVATION --partition gpu-large srun_maestro.sh $DATABASE 1
sleep 1
sbatch --reservation $RESERVATION --partition gpu-large srun_maestro.sh $DATABASE 0
sleep 1
sbatch --reservation $RESERVATION --partition gpu-large srun_maestro.sh $DATABASE 0
sleep 1
sbatch --reservation $RESERVATION --partition gpu-large srun_maestro.sh $DATABASE 0
sleep 1
sbatch --reservation $RESERVATION --partition gpu-large srun_maestro.sh $DATABASE 0
