#! /bin/bash
#
# Renew the voms proxy
#
# First do:
#   grid-proxy-init -valid 168:00
#   voms-proxy-init -valid 168:00  -out /tmp/x509up_u`id -u`_novoms
#   cp /tmp/x509up_u`id -u`_novoms $HOME/myVoms
# and then run scinet_cron_login.sh script on an external machine as a cron job.  
# Make sure to change path references in all related files accordingly.
#
# Do not run this script in the same session / window as pyfactory
# since it redefines the X509_USER_PROXY env.

# Load the GRID tools
# (If this file is not found, you probably need to email 
# support@scinet.utoronto.ca to re-mount the disk.)
if [ "$HOSTNAME" == "gpc-logindm01" ]; then
    source /scinet/lcg/grid/userinterface/gLite/etc/profile.d/grid_env.sh
fi

if [ ! -e /tmp/x509up_u`id -u`_novoms ]; then
  cp $HOME/myVoms/x509up_u`id -u`_novoms /tmp/x509up_u`id -u`_novoms
fi

export X509_USER_PROXY=/tmp/x509up_u`id -u`_novoms

voms-proxy-init -voms t2k.org:/t2k.org/Role=production -out /tmp/x509up_u`id -u` -valid 168:00 -noregen

exit
