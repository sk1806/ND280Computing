#!/bin/bash

# Quick script to be run daily by CRON to copy cleanup logs
# to t2k_logs/cleanup
source ~/T2K/GRID/nd280Computing/data_scripts/cronGRID.sh

cleanup_logs=/opt/ppd/t2k/users/stewartt/t2k_logs/www/cleanup/

if [ ! -e $cleanup_logs ]; then
    echo "$cleanup_logs doesn't exist"
    exit 1
fi

if [ -z  "$(ls $ND280TRANSFERS/clean_*log)" ]; then
    echo "No logs to archive"
    exit
fi

if [ ! -e $ND280TRANSFERS/cleaned ]; then
    echo "Making folder $ND280TRANSFERS/cleaned"
    mkdir -p $ND280TRANSFERS/cleaned
fi

# First generate the truncated report
for log in $(ls $ND280TRANSFERS/clean_*.log)
do 
    if [[ $log == *.reg.log ]]; then
	echo "Ignoring registration log $log"
	continue
    fi
    echo "Compressing $log into ${log/.log/.txt}"
    egrep -i -w 'clear|cleaning|cleared|examining|finish|interesting|iteration|removal|start|success' $log > ${log/.log/.txt}
done

# Then copy any active logs to 'cleaned' directory
cp -fv $ND280TRANSFERS/clean_*.log $ND280TRANSFERS/cleaned
mv -fv $ND280TRANSFERS/clean_*.txt $ND280TRANSFERS/cleaned

# Upload logs to web
tar --exclude='*.reg.log' -uzvf $ND280TRANSFERS/cleaned/archive.tgz $ND280TRANSFERS/cleaned/*.log
cp -fv  $ND280TRANSFERS/cleaned/archive.tgz $cleanup_logs
cp -fv  $ND280TRANSFERS/cleaned/*.txt $cleanup_logs

# Remove logs > 7 days old
let now=$(date +%s)
let day=24*3600*7
for log in $(ls $ND280TRANSFERS/clean_*.log)
do 
    let old=$(stat -c %Z $log)
    let age=$(expr $now - $old)
    #echo "Age of $log is $age"
    if(($age>$day)); then
	echo "Removing $log"
	rm -fv $log
    fi
done  
