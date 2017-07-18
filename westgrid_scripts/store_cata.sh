#!/bin/bash
#
# basic command:
# storeND280FileCatalogue -p t2kwrite -l /grid/t2k.org/nd280/production005/G/fpp/ND280/00008000_00008999/anal . d
#
# cd .../cata
# source ~/t2k-software/Run_At_Start_T2k_vXXrYY.sh
# source  ~/t2k-software/work-vXXrYY/nd280Control/*/cmt/setup.sh 
# ./store_cata.sh 
 
for nm in cali reco anal; do
  [ -d $nm ] || mkdir $nm
  mv *_${nm}_*.dat ${nm}/

  loc=$PWD
  loc=${loc#/global/scratch/t2k/}
  loc=${loc%/cata}

 cd $nm
 pwd
 storeND280FileCatalogue -p t2kwrite -l /grid/t2k.org/nd280/$loc/${nm} . d
 cd ..
done
