#!/bin/bash
#
# get_numc files 
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

    $0 DirName MyPath NumMin NumMax  ListOfFiles

This script will get files from T2KSRM in the directory DirName where the file names are
found in a file called ListOfFiles.
It will loop on the list of files starting at NumMin until NumMax files have been transferred.
For each file it will copy it from T2KSRM.nd280.org to the 
directory MyPath/DirName

Ex: $0 production004/B/mcp/neut/2010-11-air/basket/ncpiplus/reco /home/t2k/scratch/   1 20 mylist.list

EOF
}

################################################################
#Copy files
copy_files() {
    declare -i LoopCount=1
    declare -i LoopMax=$NumMax
    let LoopMax+=2
    for file in $(cat $ListFile); do
	if ((  "$LoopCount" > $NumMin )); then
	    if (( "$LoopCount" < $LoopMax)); then
		echo " "
		echo $file
		$GlobusCom  ${SourcePrefix}${DirName}/$file   file://$DestDir/$File
	    else
		return 0
	    fi;
	fi;
	let LoopCount+=1
    done
}

################################################################
# Main 

if [ $# -eq 0 ]; then
   usage >&2
   exit 1
fi


#example globus copy command
#globus-url-copy -vb gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/production004/B/mcp/neut/2010-11-air/basket/ncpiplus/reco/oa_nt_xxx_90205000-0000_wgnqdumhpok4_reco_000_prod004basket201011airncpiplus.root file:///global/scratch/t2k//production004/B/mcp/neut/2010-11-air/basket/ncpiplus/reco/

DirName=$1
DestPrefix=$2
NumMin=$3
NumMax=$4
ListFile=$5

SourcePrefix="gsiftp://t2ksrm.nd280.org//pnfs/nd280.org/data/nd280data/"
GlobusCom="globus-url-copy -v -rst -rst-retries 5 -stall-timeout 20 -sync -sync-level 1 "


# check if destination directory exists
DestDir="${DestPrefix}/${DirName}"
test -d $DestDir || { mkdir -p $DestDir; echo "Will create  directory $DestDir"; }
test -d $DestDir || { echo "Could not create directory, exit"; exit 1; }

echo Starting  `date`
copy_files
#
echo Done  `date`
exit 0





#	if [ ! `$GlobusCom  ${SourcePrefix}${DirName}/$file   file://$DestDir/$File` ]; then
#	    echo "Error transferring ${file}" >> ${ListFile}.err
#	fi
