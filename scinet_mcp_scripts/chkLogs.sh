#!/bin/bash 
#
#############################################################################
#
# Title: SciNet log Checking Script
#
# Usage: This script should be called from the specific sample directory
#        ./chkLogs.sh <Run start> <Subrun start> <Run end> <Subrun end> <optional: mon_yes/mon_no> <optional: onestage>
#
#        It will check for fatal errors, and ensure events read/written 
#        match at every stage. The total runND280 processing time is stored
#        in a file named runtimes_<Run start>-<Run end>.txt in the current
#        directory. Subruns with errors or missing logs are listed in a file
#        named errfile_<Run start>-<Run end>.txt
#
#        Optional option "mon" enables 'curl' for uploading to processing status
#        page here: https://neut00.triumf.ca/t2k/processing/status
#
# Limitations: This script assumes there is only one log file in the 
#              run/subrun directory, corresponding to the full ND280 
#              software chain.
#
#############################################################################


# Check run number arguments
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: <script> RUNSTART SUBRUNSTART RUNEND SUBRUNEND"
    exit 1
fi

# MC run number starts with 9 and is 8 digits
RUNSTART=9`printf "%07d" $1`
  RUNEND=9`printf "%07d" $3`

SUBRUNSTART=$2
  SUBRUNEND=$4

SEND_MON="$5"
ONE_STAGE="$6"

if [ "$SEND_MON" != "" ]; then
if [[ "$SEND_MON" != "mon_yes" && "$SEND_MON" != "mon_no" ]]; then
    echo "Argument 5 must be \"mon_yes\" or \"mon_no\""
    exit 1
fi
fi


# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh

if [ "${SEND_MON}" == "mon_yes" ]; then
export PATH=${PRODUCTION_DIR}:${PATH}
fi

# Get MC details from path
get_mc_details

set_run_numbers
set_comment


# Name of file to output the results to 
# (Warning: This will remove an existing file)
OUTFILE=${HERE}/runtimes_$RUNSTART-$RUNEND.txt
if [ -e $OUTFILE ]; then
    rm $OUTFILE
fi

# Error file for output of chkLogs.sh which searches for 
# files that failed processing. This file is then used as
# input to grid_cp.sh to skip attempts to copy the file to 
# the GRID, and to sub_nd280.sh if you wish to reprocess 
# missing files.
ERR_FILE=${HERE}/errfile_$RUNSTART-$RUNEND.txt
if [ -e $ERR_FILE ]; then
    rm $ERR_FILE
fi

# Create the file so that grid_cp.sh knows you ran this script
touch $ERR_FILE


# Directory for processing status webpage
if [[ $VERIFY -eq 1 ]]; then
    MON_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}

# Final production files
else
    MON_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}

fi


for (( run=${RUNSTART}; run<=${RUNEND}; run++ ))
  do	
  
  for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
    do
    
    FULL_PATH=${HERE}/${run}/${subrun}
    
    subrun_label=`printf "%04d" ${subrun}`

    log=`ls -1 ${FULL_PATH}/oa_*_*_${run}-${subrun_label}*.log`

    # Make sure the file has non-zero size. This typically occurs when the job 
    # is killed prematurely before runND280 can append to the file.
    if [ -s "${log}" ]; then
	
        # Look for any fatal errors by grep'ing for the case-insensitive string "fatal"
	# (since MySql errors contain "fatal" and parses differently)
	FATAL_ERROR=`grep FATAL ${log} | cut -d' ' -f3`
	if [ "$FATAL_ERROR" != "" ]; then
	    echo "$run ${subrun_label} Fatal error in ${FATAL_ERROR}" 2>&1 | tee -a $ERR_FILE
	    
	else

            # Events read/write only for ND280 processing
            if [ ${STEP} == nd280 ]; then

                # Check that the number of events Read and Written match at every istep (module)
                EVENT_MATCH=1

                # Store the number of events read in by ND280MC
		NUM_G4_EVENTS=`grep "Number of events" ${log} | cut -d' ' -f6`

		# ND280MC failed to produce events
                if [ "${ONE_STAGE}" == "" ]; then
		if [ "$NUM_G4_EVENTS" == "" ]; then
		    echo "$run ${subrun_label} Fatal error in nd280MC (0 Events)" 2>&1 | tee -a $ERR_FILE
                    EVENT_MATCH=0

		# ND280MC completed with some number of events
		else

                    # Following ND280MC, runND280 records the number of events read and written by
                    # each module. Store these in arrays.
		    EVENTS_READ=(`grep "Total Events Read" ${log} | cut -d' ' -f4`)
		    EVENTS_WRITE=(`grep "Total Events Written" ${log} | cut -d' ' -f4`)

		    STAGES=(ELECSIM CALIBRATION RECONSTRUCTION ANALYSIS)

		    for (( istep=0; istep<4; istep++ ))
		      do

                      # Events read in at every istep should be the same
		      if [ ${EVENTS_READ[${istep}]} != ${NUM_G4_EVENTS} ]; then                                                                               
			  echo "$run ${subrun_label} Read events = ${EVENTS_READ[${istep}]} != ${NUM_G4_EVENTS} at ${STAGES[${istep}]}" 2>&1 | tee -a $ERR_FILE
			  EVENT_MATCH=0
			  break
		      fi
		      
                      # Events written at every istep, except oaAnalysis, should be the same
		      if [ ${EVENTS_WRITE[${istep}]} != ${NUM_G4_EVENTS} -a $istep -lt 3 ]; then     
			  echo "$run ${subrun_label} Write events = ${EVENTS_WRITE[${istep}]} != ${NUM_G4_EVENTS} at ${STAGES[${istep}]}" 2>&1 | tee -a $ERR_FILE
			  EVENT_MATCH=0
			  break
			  
                      # Events written by oaAnalysis should be 0 (since it's not writing oaEvent events)
		      elif [ ${EVENTS_WRITE[${istep}]} != 0 -a $istep -eq 3 ]; then    
			  echo "$run ${subrun_label} Write events = ${EVENTS_WRITE[${istep}]} != 0 at ${STAGES[${istep}]}" 2>&1 | tee -a $ERR_FILE
			  EVENT_MATCH=0
			  break
		      fi
		      
		    done
		    
		fi
		
            # Checking 'numc' files
	    elif [ ${STEP} == numc ]; then
                 
                EVENT_MATCH=1             

		FATAL_ERROR=`grep -i aborted ${log} | cut -d' ' -f5`
		if [ "$FATAL_ERROR" != "" ]; then
		    echo "$run ${subrun_label} Aborted" 2>&1 | tee -a $ERR_FILE
		    EVENT_MATCH=0
		fi
		
            fi
            fi
              
            # Get total runtime recorded by runND280 if there were no problems
	    if [ $EVENT_MATCH == 1 ]; then
		RUNTIME=`grep "Total Processing Time" ${log} | cut -d' ' -f4`
	    
                # If runND280 failed to record a total runtime, e.g. if the job was killed prematurely
		if [ ! -n "$RUNTIME" ]; then
		    echo "$run ${subrun_label} -99999" 2>&1 | tee -a $ERR_FILE
		    
                # Runtime found. Convert from seconds to hours and output to file
		else
		    RUNTIME=`echo "scale=2; ${RUNTIME}/3600" | bc`
		    echo $run ${subrun_label} ${RUNTIME} 2>&1 | tee -a $OUTFILE
		    
		fi
	    fi

	    

	fi

	# Send processing info to status page
	if [[ ${STEP} == nd280 && ${SEND_MON} == "mon_yes" ]]; then
	    ${PRODUCTION_DIR}/./send_mon_info.pl ${run} ${subrun_label} MCP ${FULL_PATH} ${MON_DIR} > /dev/null
	fi

	
    # If we failed to find a valid (non-zero sized) .log file
    else
	echo $run ${subrun_label} "No log!" 2>&1 | tee -a $ERR_FILE
	
    fi
    
  done
  
done
