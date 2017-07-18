#!/bin/bash
#

### Uncomment line below when debugging - will expand all commands   
#set -x  

################################################################

usage() {
    cat - <<EOF
Usage:  

    $0 Type DirPath  ListName

This script will put files on T2KSRM in the directory $DirPath/$Type where the file names are
found in file ListName and will register each file in the LFC

Ex: $0  anal production005/A/rdp/verify/v10r9p1/ND280/00007000_00007999 run7xxx_anal_a.list  >& register_run7xxx_anal_a.log

EOF
}
################################################################

if [ $# -eq 0 ]; then
   usage >&2
   exit 1
fi


#example globus copy command
#globus-url-copy -vb -cd  file:///global/scratch/t2k/production004/C/mcp/genie/2010-11-water/basket/beam/anal/oa_gn_beam_91211000-0000_c5j2mmpu7dea_anal_000_prod004basket201011water-bsdv01.root gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/production004/C/mcp/genie/2010-11-water/basket/beam/anal/
#lcg-rf -l lfn:/grid/t2k.org/nd280/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root   srm://t2ksrm.nd280.org/nd280data/production004/C/mcp/genie/2010-11-air/basket/beam/anal/oa_gn_beam_91201002-0110_y4ev2jrrttrk_anal_000_prod004basket201011air-bsdv01.root

Type=$1
echo Type: $Type
DirPath=$2
echo DirPath: $DirPath
ListName=$3 
echo ListName: $ListName

LfnPrefix="lfn:/grid/t2k.org/nd280/"
Command="lcg-rf -l  "
RegSourceDir=srm://t2ksrm.nd280.org/nd280data/$DirPath/$Type
echo RegSourceDir: $RegSourceDir
RegDestDir=$LfnPrefix$DirPath/$Type
echo RegDestDir: $RegDestDir

DestPrefix="gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/"
GlobusCom="globus-url-copy  -cd -rst "

SourceDir="/global/scratch/t2k/$DirPath/${Type}"
echo SourceDir: $SourceDir
DestDir="${DestPrefix}/${DirPath}/${Type}"
echo DestDir: $DestDir
test -d $SourceDir || { echo "Could not open directory $SourceDir exit"; exit 1; }

for file in $(cat $ListName); do
    echo " "
    echo $file
    $GlobusCom file://${SourceDir}/$file   $DestDir/$File
    $Command $RegDestDir/$file     $RegSourceDir/$file
done
#
echo Done
exit 0
