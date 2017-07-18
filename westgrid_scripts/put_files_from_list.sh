#!/bin/bash
#

### Uncomment line below when debugging - will expand all commands   
#set -x  

################################################################

usage() {
    cat - <<EOF
Usage:  

    $0 Type DirPath ListName

This script will put files on T2KSRM in the directory $DirPath/$Type where the file names are
found in a file $Type_$DirName.list where DirName is DirPath where "/" are replaced by "_"

Ex: $0  anal production004/C/mcp/genie/2010-11-air/basket/beam  XXXX.list > copy_genie_2010-11-air_basket_beam.log

EOF
}

if [ $# -eq 0 ]; then
   usage >&2
   exit 1
fi


#example globus copy command
#globus-url-copy -vb -cd  file:///global/scratch/t2k/production004/C/mcp/genie/2010-11-water/basket/beam/anal/oa_gn_beam_91211000-0000_c5j2mmpu7dea_anal_000_prod004basket201011water-bsdv01.root gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/production004/C/mcp/genie/2010-11-water/basket/beam/anal/

Type=$1
echo Type: $Type
DirPath=$2
echo DirPath: $DirPath
ListName=$3
echo ListName: $ListName

DestPrefix="gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data"
GlobusCom="globus-url-copy -cd -rst "

SourceDir="/global/scratch/t2k/$DirPath/${Type}"
echo SourceDir: $SourceDir
DestDir="${DestPrefix}/${DirPath}/${Type}"
echo DestDir: $DestDir
test -d $SourceDir || { echo "Could not open directory $SourceDir exit"; exit 1; }

for file in $(cat $ListName); do
    echo " "
    echo $file
    $GlobusCom file://${SourceDir}/$file   $DestDir/$File
done
#
echo Done
exit 0
