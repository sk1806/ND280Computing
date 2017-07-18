#!/bin/bash

j=$1

while qstat $j >& /dev/null; do
    date
    qstat -f $j | fgrep 'used.'
    sleep 300
done
