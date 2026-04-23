#!/bin/bash

DATABASE=$1
MASTER=$2 # should be 0 or 1



source /home/joao.pinto/public/server/setup_grid.sh $DATABASE


if [[ $MASTER -eq 1 ]];
then
    echo "Running as master node"
    maestro.py pilot run -m 
else
    echo "Running as slave node"
    maestro.py pilot run
fi
