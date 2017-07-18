#!/bin/bash

source ~/.bashrc

export ND280COMPUTINGROOT=~/T2K/GRID/nd280Computing
#export PATH=/usr/local/matlab/bin:/usr/java/j2sdk1.4.2_12/bin:/home/perkin/bin:/opt/d-cache/srm/bin:/opt/d-cache/dcap/bin:/opt/edg/bin:/opt/glite/bin:/opt/globus/bin:/opt/lcg/bin:/usr/compilers/4.3.2/bin:/usr/local/matlab/bin:/usr/java/j2sdk1.4.2_12/bin:/home/perkin/bin:/usr/lib64/qt-3.3/bin:/usr/kerberos/bin:/usr/compilers/4.3.2/bin:/usr/local/bin:/usr/bin:/bin:/usr/X11R6/bin:/usr/local/t2k-software/CMT/v1r20p20081118/Linux-x86_64
export PATH=$PATH:/usr/lib64/qt-3.3/bin:/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/ppd/stewartt/bin
export ROOTSYS=/opt/ppd/t2k/users/stewartt/T2K/GRID/root_v5.34.36
. $ROOTSYS/bin/thisroot.sh
export PYTHONPATH=/usr/local/root/lib:/usr/lib/python2.6/site-packages:/home/ppd/stewartt/T2K/GRID/nd280Computing
export LCG_LOCATION=/usr
export VO_T2K_ORG_DEFAULT_SE=heplnx204.pp.rl.ac.uk
export MYPROXY_SERVER_RAL=myproxy.gridpp.rl.ac.uk
export MYPROXY_SERVER_CERN=myproxy.cern.ch
export MYPROXY_SERVER=$MYPROXY_SERVER_CERN
export LCG_GFAL_INFOSYS=lcgbdii.gridpp.rl.ac.uk:2170,lcg-bdii.gridpp.ac.uk:2170,topbdii.grid.hep.ph.ic.ac.uk,lcg-bdii.cern.ch:2170
export DPM_HOST=$VO_T2K_ORG_DEFAULT_SE
export DPNS_HOST=$VO_T2K_ORG_DEFAULT_SE

source $ND280COMPUTINGROOT/setup.sh
