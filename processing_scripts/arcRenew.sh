#!/bin/bash

# simple bash script to renew job proxies on ARC CEs

source ~/t2k/GRID/nd280Computing/data_scripts/cronGRID.sh

CEs=(arc-ce01.gridpp.rl.ac.uk
     arc-ce02.gridpp.rl.ac.uk
     arc-ce03.gridpp.rl.ac.uk
     arc-ce04.gridpp.rl.ac.uk
     arc-ce05.gridpp.rl.ac.uk
     t2arc01.physics.ox.ac.uk
     hepgrid2.ph.liv.ac.uk)


for CE in ${CEs[@]}; do
    arcsync -c ${CE} -f

    # only renew running or queued jobs
    for status in Q R; do 
	arcrenew -c ${CE} -s INLRMS:${status}
    done

    # clean failed or deleted jobs
    for status in DELETED FAILED; do 
	arcclean -c ${CE} -s INLRMS:${status}
    done
done
