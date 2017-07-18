#!/bin/bash

cd /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts
source ./cronGRID.sh
#grep the output of myproxy-info for the term time left
#if there is no value for timeleft something is wrong
#if there is less than 1 day left e-mail the user
myproxy-info -v -d -s $MYPROXY_SERVER -k renew | grep timeleft
output=$(myproxy-info -v -d -s $MYPROXY_SERVER -k renew | grep timeleft)
if [[ -n $output ]]; then
    output=${output#*(}
    output=${output%)*}
    timeleft=$(echo $output | cut -d ' ' -f1)
#    if [ $timeleft -lt 1.0 ]; then
    if (( $(echo "$timeleft < 1.0" |bc -l) )); then
	mail -s "MyProxyWatcher: Less than one day left for MyProxy Credentials" trevor.stewart@stfc.ac.uk <<< "MyProxyWatcher: There are $timeleft days left for your MyProxy credentials."
    fi
else
    mail -s "MyProxyWatcher: expired myproxy" trevor.stewart@stfc.ac.uk <<< "MyProxyWatcher: expired myproxy"

fi
