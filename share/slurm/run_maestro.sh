#!/bin/bash


MASTER=$1 # should be 0 or 1
GPUS=$2
CPUS=$3


# setup orchestra env
source /mnt/market_place/services/orchestra-server/setup_grid.sh


if [[ $MASTER -eq 1 ]];
then
    echo "Running as master node"
    maestro.py pilot run --gpus $GPUS --cpus $CPUS -m 
else
    echo "Running as slave node"
    maestro.py pilot run --gpus $GPUS --cpus $CPUS
fi
