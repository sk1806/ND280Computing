#!/bin/bash

cd /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts
source ./cronGRID.sh
./RemoveFailedFTS.py "$1"
