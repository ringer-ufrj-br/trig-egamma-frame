
RESERVATION=joao.pinto_13
DATABASE=ringer

sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh $DATABASE 1
sleep 1
sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh $DATABASE 0
sleep 1
#sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh $DATABASE 0
sbatch --partition cpu-large srun_maestro.sh $DATABASE 0

