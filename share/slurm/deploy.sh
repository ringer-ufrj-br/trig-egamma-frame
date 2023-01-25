
RESERVATION=joao.pinto_4

sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh 1 0 5
sleep 1
sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh 0 0 20
sleep 1
sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh 0 0 20
sleep 1
sbatch --reservation $RESERVATION --partition cpu-large srun_maestro.sh 0 0 20
