#!/bin/bash
# Usage:
# cd dir_with_files
# $0 file 6Ar8 cata # puts "file" to T2KSRM to production006/A/rdp/ND280/00008000_00008999/cata directory
#
# example globus copy command
#globus-url-copy -vb -cd  file:///global/scratch/t2k/production004/C/mcp/genie/2010-11-water/basket/beam/anal/oa_gn_beam_91211000-0000_c5j2mmpu7dea_anal_000_prod004basket201011water-bsdv01.root gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/production004/C/mcp/genie/2010-11-water/basket/beam/anal/
#lcg-rf -l lfn:/grid/t2k.org/nd280/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root   srm://t2ksrm.nd280.org/nd280data/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root

SrmPfx=srm://t2ksrm.nd280.org/nd280data
LfnPfx=lfn:/grid/t2k.org/nd280
LocPfx=/global/scratch/t2k

file=$1
code=$2
type=$3
pn=${code:0:1}
sp=${code:1:1}
pp=${code:2:1}
rn=${code:3:2}
echo $pn $sp $pp $rn

if [[ $pp == "f" ]]; then
  pp=fpp
elif [[ $pp == "r" ]]; then
  pp=rdp
else
  echo Unknown processing type code $pp
  return 1
fi
rr=0000${rn}
rr=${rr: -5}
rr=${rr}000_${rr}999

ffile=$file
file=$(basename $file)

DirPath=production00${pn}/${sp}/${pp}/ND280/${rr}/${type}
echo lcg-cr -v -d $SrmPfx/$DirPath/$file -l ${LfnPfx#lfn:}/$DirPath/$file file://$ffile
#read -n1 -p "Proceed ?[Y/N] " ans
#if ! [[ $ans == y || $ans == Y ]]; then exit 1; fi 
lcg-cr -v -d $SrmPfx/$DirPath/$file -l ${LfnPfx#lfn:}/$DirPath/$file file://$ffile
return 0
