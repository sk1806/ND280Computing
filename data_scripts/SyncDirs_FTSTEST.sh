#!/bin/bash


source /cvmfs/ganga.cern.ch/dirac_ui/bashrc


cd /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts
source ./cronGRID.sh
export FTS_SERVICE=https://lcgfts3.gridpp.rl.ac.uk:8446

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ppd/t2k/users/stewartt/boost_1_48_0/stage/lib/


./SyncDirs_FTSTEST.py -a lfn:/grid/t2k.org/test/Trevor20170707_FTS3_REST_Test/ -b srm://t2ksrm.nd280.org/nd280data/test/Trevor20170707_FTS3_REST_Test/ -f 1
