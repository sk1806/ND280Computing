#!/bin/bash

# simple wrapper script for DumpFiles.py


# lfcroot=/grid/t2k.org/nd280/production006/A/rdp/verify/v11r21/ND280
# for run in 6 7 8; do
#     for stage in anal reco; do
#         lfcdir=$lfcroot/0000${r}000_0000${r}999/controlsample/$stage
# 	list=${run}k.controlsample.${stage}.list
# 	for file in $(lfc-ls $lfcdir); do
# 	    echo lfn:$lfcdir/$file
# 	done  > $list
# 	./DumpFiles.py --tier=T1 --filelist=$list --fts=1 --repreg=REP
#     done
# done

lfcroot=/grid/t2k.org/nd280/production006/A/mcp/verify/v11r21/old-neut/2010-11-air

for region in basket magnet; do
    lfcdir=$lfcroot/$region/run3/reco
    list=old-neut.$region.reco.list

    for file in $(lfc-ls $lfcdir); do
	echo lfn:$lfcdir/$file
    done  > $list
    ./DumpFiles.py --tier=srmv2.ific.uv.es --filelist=$list --fts=1 --repreg=REP
done
  


# wait a few hours
sleep 12h

# for run in 6 7 8; do
#     for stage in anal reco; do
# 	list=${run}k.controlsample.${stage}.list
# 	./DumpFiles.py --tier=T1 --filelist=$list --repreg=REG
#     done
# done

for region in basket magnet; do
   list=old-neut.$region.reco.list
   ./DumpFiles.py --tier=srmv2.ific.uv.es --filelist=$list --fts=1 --repreg=REP
done
 

exit 0