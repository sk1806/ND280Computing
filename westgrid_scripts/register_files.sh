#!/bin/bash
#
# register files into LFC catalog 
#
# Input params: see usage below
# 
#

### Uncomment line below when debugging - will expand all commands   
#set -x  

################################################################

usage() {
    cat - <<EOF
Usage:  

    $0 Type DirPath ListName

This script will register files residing on T2KSRM in the directory "Prefix/DirPath/Type"
It expects to find a list of files to register in file ListName

Ex: ./register_files.sh anal production005/A/rdp/verify/v10r5/ND280/00007000_00007999 anal_test.list

EOF
}

if [ $# -eq 0 ]; then
   usage >&2
   exit 1
fi

#Example: lcg-rf -l lfn:/grid/t2k.org/nd280/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201000-0000_ehrjn445bzm4_anal_000_prod004basket201011air-bsdv01.root   srm://t2ksrm.nd280.org/nd280data/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201000-0000_ehrjn445bzm4_anal_000_prod004basket201011air-bsdv01.root

#         lcg-rf -l lfn:/grid/t2k.org/nd280/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root   srm://t2ksrm.nd280.org/nd280data/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root

Type=$1
DirPath=$2
ListName=$3 
#echo ListName: $ListName

LfnPrefix="lfn:/grid/t2k.org/nd280/"
Command="lcg-rf -l  "

SourceDir=srm://t2ksrm.nd280.org/nd280data/$DirPath/$Type
echo SourceDir: $SourceDir
DestDir=$LfnPrefix$DirPath/$Type
echo DestDir: $DestDir

for file in $(cat $ListName); do
    echo " "
    echo $file
    $Command $DestDir/$file     $SourceDir/$file
    ##echo "$Command $DestDir/$file     $SourceDir/$file"
done
#
echo Done
exit 0
