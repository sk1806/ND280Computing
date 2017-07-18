#!/bin/bash
#pth=production006/A/fpp/verify/v11r21/ND280
#pth=production006/B/rdp/ND280
#pth=production006/C/fpp/ND280
#pth=production006/C/pc1/ND280
#pth=production005/F/fpp/ND280
#pth=production005/H/fpp/ND280
#pth=contrib/tcp-calib-test-2014
#pth=contrib/tcp-timing-calib-test-201402
#pth=production006/E/fpp/ND280
#pth=production006/E/pc1/ND280
pth=production006/I/rdp/ND280

if [[ $(hostname -s) != "bugaboo-fs" ]]; then
   echo "This script MUST be run on bugaboo-fs"
   return 1
fi

type=$1

rr=$2
rr1=0000${rr}
rr1=${rr1: -5}
rr1=${rr1}000_${rr1}999

trig=$3

if (( $# < 2 )); then
   echo "Usage: $0 type range"
   echo "E.g. : $0 anal 6 [spl/cos]"
   return 1
fi

if [[ $trig == spl ]]; then
    rex=_spl_
elif [[ $trig == cos ]]; then
    rex=_cos_
else
    rex=""
fi

echo $rex

wdir=/global/scratch/t2k/${pth}/${rr1}/${type}
lfil=${type}${rr}_$(ls -1 $wdir | fgrep "$rex" |  wc -l)tmp.list
ls -1 $wdir | fgrep "$rex"  >| $lfil

rsync -av $lfil vavilov@neut19.triumf.ca:work/nd280/westgrid_scripts/


./put_files_from_list.sh $type ${pth}/${rr1} $lfil >& ${lfil%.list}.log &
tail -f ${lfil%.list}.log
