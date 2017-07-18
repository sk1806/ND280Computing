#!/bin/bash
#
#############################################################################
#
# Title:  SciNet MCP Progress Page Generator
#
# Usage: ./mk_progress_page.sh <RUNSTART> <SUBRUNSTART> <RUNEND> <SUBRUNEND>
#        This creates a page corresponding to the current working directory 
#        here: https://neut00.triumf.ca/t2k/processing/status
#
#############################################################################


# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: ./mk_progress_page.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND"
    exit 1
fi

# MC run number starts with 9 and is 8 digits
RUNSTART=9`printf "%07d" $1`
  RUNEND=9`printf "%07d" $3`

SUBRUNSTART=$2
  SUBRUNEND=$4


# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh
. ${PRODUCTION_DIR}/grid_header.sh


# Directory for storing the log
LOG_DIR=${HERE}/progress_logs
mkdir -p ${LOG_DIR}
LOG_FILE=${LOG_DIR}/mk_progress_page.log

echo "Running Progress Page Generation for..."
get_mc_details

set_run_numbers

# Set run list
RUN_LIST=${LOG_DIR}/list_good_runs.txt
if [ -e ${RUN_LIST} ]; then
    rm ${RUN_LIST}
fi

for (( run=${RUNSTART}; run<=${RUNEND}; run++ ))
do
    for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
    do

        echo "${run} ${subrun}" >> ${RUN_LIST}

    done
done



# Add "verify/nd280vers" to the GRID sample directory for verification files
if [[ $VERIFY -eq 1 ]]; then
    SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
    
# Final production files
else
    SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
fi

#FULL_COMMAND="curl -k --header \"Accept: text/plain\" --data-binary @${RUN_LIST} -X PUT \"https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/${SAMPLE_DIR}\""

FULL_COMMAND="curl -k --header \"Accept: text/plain\" --data-binary @${RUN_LIST} -X POST \"https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/${SAMPLE_DIR}?SPILL\""

echo ${FULL_COMMAND} > $LOG_FILE

if [ $SUBJOB_FOR_REAL -eq 1 ]; then
    #curl -k --header "Accept: text/plain" --data-binary @${RUN_LIST} -X PUT "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/${SAMPLE_DIR}" >> $LOG_FILE 2>&1

curl -k --header "Accept: text/plain" --data-binary @${RUN_LIST} -X POST "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/${SAMPLE_DIR}?SPILL" >> $LOG_FILE 2>&1

    #${FULL_COMMAND} >> $LOG_FILE 2>&1
fi
