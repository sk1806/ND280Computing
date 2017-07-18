#!/bin/bash

rm -f tmpjid

echo 'dumping autowms.conf - please verify configuration!'
cat autowms.conf

for ce in $(cat ce.list); do
    command="glite-wms-job-submit -a -c autowms.conf -o tmpjid -r $ce softwareTest.jdl"
    echo $command
    $command
done
