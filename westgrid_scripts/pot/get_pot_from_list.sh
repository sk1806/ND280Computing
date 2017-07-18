#!/bin/bash
#

### Uncomment line below when debugging - will expand all commands   
#set -x  

################################################################

usage() {
    cat - <<EOF
Usage:  

    $0 Type DirPath ListName

This script will produce POT numbers for files in the directory \$DirPath/\$Type where the file names are
found in a file \$ListName.

Ex: $0  anal production006/A/rdp/verify/v11r19/ND280/00008000_00008999 anal8_7005tmp.list > pot_7005.list
EOF
}

if [ $# -eq 0 ]; then
   usage >&2
   exit 1
fi

Type=$1
#echo Type: $Type
DirPath=$2
#echo DirPath: $DirPath
ListName=$3
#echo ListName: $ListName

DestPrefix="gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data"
SourceDir="/global/scratch/t2k/$DirPath/${Type}"

#echo SourceDir: $SourceDir
#DestDir="${DestPrefix}/${DirPath}/${Type}"
#echo DestDir: $DestDir
test -d $SourceDir || { echo "Could not open directory $SourceDir exit"; exit 1; }

for file in $(cat $ListName); do
    echo -n $file
    root -l -n -q 'get_pot_for_file.cpp("'${SourceDir}/${file}'")' 2> /dev/null | tail -1 | awk '{printf " %s %s\n",$1,$2}'
done

exit 0
