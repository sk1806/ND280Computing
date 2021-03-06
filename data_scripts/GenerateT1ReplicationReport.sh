#!/bin/bash

cd /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts
source cronGRID.sh

std_out=$ND280TRANSFERS/replication.T1.$(date +%H).out
std_err=$ND280TRANSFERS/replication.T1.$(date +%H).err

nohup ./GenerateReplicationReport.py -s T1 \
-l lfn:/CURRENT </dev/null >$std_out 2>$std_err &
