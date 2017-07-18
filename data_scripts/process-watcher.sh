#!/bin/bash

# simple script to keep track of running process(es) and delegate a proxy
# if it is due to expire

# if no arg specified then assume your tracking cleanup scripts
if [ -z "$1" ]; then
    toGrep="t2k"
# otherwise grep for arg
else
    toGrep="$1"
fi

# run in perpetuity
while [ 1 ]; 
  do 
  ps ux | grep $toGrep
  voms-proxy-info
  ./check-voms.sh 
  sleep 60 
done
