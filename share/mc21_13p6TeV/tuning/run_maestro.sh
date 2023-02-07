#!/bin/bash


MASTER=$1 # should be 0 or 1



source /home/joao.pinto/public/server/setup_grid.sh


if [[ $MASTER -eq 1 ]];
then
    echo "Running as master node"
    maestro.py pilot run -m 
else
    echo "Running as slave node"
    maestro.py pilot run
fi
