#!/bin/bash

# Place this file in the root flux directory, e.g. where <root flux dir>/[nd5, nd6, sk]

# Uncomment the following for hadd'ing 11a nd6 files
dir=13a_nom_ND6_250ka
FILE_START=0
FILE_END=300

# Following for 11a nd5 files
#dir=nd5
#FILE_START=0
#FILE_END=499



cd $dir

mkdir -p hadd

cd root

ROOTNAME=nu.${dir}_flukain

    # Put the files in proper order
for (( i=$FILE_START; i<=$FILE_END; i++ ))
do

    FILELIST[i]=$ROOTNAME.${i}.root
    
done

# hadd'ed file is placed in  <root flux dir>/[nd5, nd6, sk]/hadd/. along with a log file (hadd.log)
hadd -f ../hadd/nu.${dir}_flukain.$FILE_START-$FILE_END.root ${FILELIST[@]} > ../hadd/hadd.log &

cd ../..

