#!/bin/bash

# Quick script to be run daily by CRON to ensure only last 25 of each type
# of replcation report are present in t2k_logs and $ND280TRANSFERS
# The rest are archived in $ND280TRANSFERS/replicationArchive
source ~/T2K/GRID/nd280Computing/data_scripts/cronGRID.sh

t2klogs=/opt/ppd/t2k/users/stewartt/t2k_logs/www/replication
logTypes=('T1' 'ALL')


cd $ND280TRANSFERS
pwd
for log in ${logTypes[@]}
  do
  let nTotal=$(ls replication.$log.*log | wc -l)
  echo "$nTotal total log files ($log)"
  if (( $nTotal > 25 )); then
      let nMove=${nTotal}-25
  else
      # don't move anything
      echo "Nothing to move"
      break
  fi
  echo "Moving $nMove log files ($log)..."
  for file in $(ls replication.$log.*log | head -$nMove)
    do
      if [ ! -e $file ]; then
	  break
      fi
    command="mv -f $file $ND280TRANSFERS/replicationArchive/"
    echo $command
    $command
  done
done

# Clear online logs and update
rm -f $t2klogs/*.log
cp -fv $ND280TRANSFERS/replication*.log $t2klogs

# Keep a tarball of the archive online
echo "Archiving..."
tar czvf $t2klogs/archive.tgz $ND280TRANSFERS/replicationArchive
