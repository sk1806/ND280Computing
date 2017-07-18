#!/bin/bash
#pth=production006/A/fpp/verify/v11r21/ND280
#pth=production006/B/fpp/ND280
#pth=production006/C/fpp/ND280
#pth=production006/C/pc1/ND280
#pth=production005/F/fpp/ND280
#pth=production005/H/fpp/ND280
#pth=contrib/tcp-calib-test-2014
#pth=contrib/tcp-timing-calib-test-201402
#pth=production006/E/fpp/ND280
#pth=production006/E/pc1/ND280
pth=production006/I/rdp/ND280

type=$1
rr=$2
rr1=0000${rr}
rr1=${rr1: -5}
rr1=${rr1}000_${rr1}999

if (( $# < 2 )); then
   echo "Usage: $0 type range"
   echo "E.g. : $0 anal 6"
   return 1
fi


wdir=/global/scratch/t2k/${pth}/${rr1}/${type}
lfil=$(echo ${type}${rr}_*tmp.list)
if (( $(echo $lfil | wc -w) != 1 )); then
   echo "Wrong/no list file: $lfil"
   return 1
fi

./register_files.sh $type ${pth}/${rr1} $lfil  >& ${lfil%.list}.log &
sleep 2
tail -f ${lfil%.list}.log
