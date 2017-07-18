#!/bin/bash

# Set environment
source /home/ppd/stewartt/T2K/GRID/nd280Computing/data_scripts/cronGRID.sh

echo "Refreshing credentials"

# Destroy any existing voms credentials
# voms-proxy-destroy -debug

# Delegate a new short term proxy from the myproxy server with password
myproxy-get-delegation -v -d -s $MYPROXY_SERVER -k renew --stdin_pass < ~/.glite/myproxy

# Stamp the delegated credentials with voms attributes
voms-proxy-init -voms t2k.org:/t2k.org/Role=production -valid 24:0 -noregen

# Delegate the short term voms proxy to the FTS server(s)
 #glite-delegation-init -v -f -s $FTS_SERVICE -e 840
fts-delegation-init -v -s $FTS_SERVICE -e 840 
