#!/bin/bash

source /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts/cronGRID.sh

let time_left=$(voms-proxy-info --timeleft)

if [[ $time_left -le 600 || -z "$time_left" ]]; then
    ~/T2K/GRID/nd280Computing/data_scripts/get-voms.sh
else
    echo "$time_left seconds remaining"
fi
   
