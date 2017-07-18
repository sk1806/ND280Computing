#!/bin/bash

VO='t2k.org'
# remember to do:
# voms-proxy-init --voms $VO 

rm -f jobIDfile

for wms in $(lcg-infosites --vo $VO wms | grep ac.uk); do
export GLITE_WMS_WMPROXY_ENDPOINT=$wms
    for ce in $(lcg-infosites --vo $VO ce | awk '/ac.uk/{print $6}'); do
        command="glite-wms-job-submit"
	if [ ! -e $GLITE_LOCATION/etc/$VO/glite_wms.conf ] && [ -e autowms.conf ]; then
	    command="$command -c autowms.conf"
	fi
	command="$command -a -o jobIDfile -r $ce testAll.jdl"
	echo $command
	$command
    done
done 

# Then to check job status do:
#glite-wms-job-status -i jobIDfile

# Then get output with:
#glite-wms-job-output --noint -i jobIDfile
