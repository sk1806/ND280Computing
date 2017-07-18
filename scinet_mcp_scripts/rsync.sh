#!/bin/bash
#
#############################################################################
#
# Title: SciNet 
#
# Usage: Call this script in a specific sample directory:
#        ./rsync.sh <run start> <subrun start> <run end> <subrun end> <module step> 
#        where <module step>=(all g4mc elmc cali reco anal logf) where 
#        all=(cali reco anal logf).
#
#        This requires your GRID proxy to be enabled to copy into the 
#        T2K common account on silo.westgrid.ca. It uses grid enabled ssh 
#        (gsissh) to create directories on under the t2k account on silo
#        and for rsync.
#                 
#
#############################################################################


# Set remote site details
REMOTEUSER=t2k
REMOTEHOST=silo.westgrid.ca
REMOTEDIR=/home/t2k/data

if [ "$HOSTNAME" != "gpc-logindm01" ]; then
    echo "Error: Do not run on this node. Do ssh datamover1 first!"
else
    source /scinet/lcg/grid/userinterface/gLite/etc/profile.d/grid_env.sh
    export MYPROXY_SERVER=myproxy.westgrid.ca
fi



# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" || "$5" == "" ]]; then
    echo "Usage: ./rsync.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND STEP"
    exit 1
fi

# MC run number starts with 9 and is 8 digits
RUNSTART=9`printf "%07d" $1`
  RUNEND=9`printf "%07d" $3`

SUBRUNSTART=$2
  SUBRUNEND=$4


LOG_DIR=silo_logs
mkdir -p $LOG_DIR


# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh


get_mc_details


# If we're in the nd280 chain directory then grab
# the actual specified module step
if [ ${STEP} == "nd280" ]; then
    STEPS=($5)
fi

# If you specified to copy all steps, then copy 
# all files, skipping redundant g4mc and elmc types
# but all catalogue files
if [ $STEPS == "all" ]; then
    STEPS=(anal cali reco logf)
fi

# Error: You must specify a step or all to copy
if [ $STEPS[0] == "" ]; then
    echo "Must specify STEP"
    exit
fi

set_run_numbers
set_comment


CP_COMMAND="rsync"
FLAGS="-r --update --rsh=gsissh"
#FLAGS="-rv --stats --progress --update --rsh=gsissh"  # more verbose output

for (( run=$RUNSTART; run<=$RUNEND; run++ ))
  do
    for STEP in "${STEPS[@]}"
      do
       
      # Add "verify/nd280vers" to the GRID sample directory for verification files
      if [[ $VERIFY -eq 1 ]]; then
	  SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}/${STEP}

      # Final production files
      else
	  SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}/${STEP}
      fi

      LOG_FILE=${HERE}/${LOG_DIR}/${STEP}_${run}_log.txt
      if [ -e $LOG_FILE ]; then
          rm $LOG_FILE
      fi

      #echo gsissh ${SSH_FLAGS} ${REMOTEUSER}@${REMOTEHOST} "mkdir -p ${REMOTEDIR}/${SAMPLE_DIR};" >> ${LOG_FILE} 2>&1

      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
          gsissh ${SSH_FLAGS} ${REMOTEUSER}@${REMOTEHOST} "mkdir -p ${REMOTEDIR}/${SAMPLE_DIR};"
      fi

      if [ $STEP == "logf" ]; then
          FILETOFIND=oa_*_*_${run}-*_*_${STEP}_*_${COMMENT}.log
      elif [ $STEP == "anal" ]; then
          FILETOFIND=oa_*_*_${run}-*_*_${STEP}_*_${COMMENT}-bsd.root
      else
          FILETOFIND=oa_*_*_${run}-*_*_${STEP}_*_${COMMENT}.root
      fi

      # rsync all subruns together
      FULL_COMMAND="${CP_COMMAND} ${FLAGS} ${HERE}/${run}/*/${FILETOFIND} ${REMOTEUSER}@${REMOTEHOST}:${REMOTEDIR}/${SAMPLE_DIR}/"
      
      echo ${FULL_COMMAND} >> ${LOG_FILE} 2>&1
      
      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
	  ${FULL_COMMAND} >> ${LOG_FILE} 2>&1
      fi

    done # STEP

done # run
