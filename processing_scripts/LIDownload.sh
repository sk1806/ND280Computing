#!/bin/bash

source /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts/cronGRID.sh
source $ND280COMPUTINGROOT/setup.sh

if [ -e $ND280COMPUTINGROOT/processing_scripts/lidownload.list ]; then
    cd $ND280COMPUTINGROOT/data_scripts
    ./LocalCopyLFNList.py ../processing_scripts/lidownload.list
else
    echo "Cannot find lidownload.list"
fi
