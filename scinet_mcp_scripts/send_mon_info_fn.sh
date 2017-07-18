#!/bin/bash
#
# Extract relevant results from a processing job log file and send 
# the results to Simon's task which will fill the database. 
#
# Based on Ashok's script ashok-total-log-v9r7p1.sh*
#
# Input:  RUNNUMBER subrun TYPE (spl or cos)  LOG_DIR 
#

function send_mon_info_fn {

 
#run=$1
#subrun=$2
#type=$3
type=spl  # use 'spl' for MC 
if [ $type == "spl" ]; then
    TYPE="SPILL"
elif [ $type == "cos" ]; then
    TYPE="COSMIC"
else
    TYPE="UNKNOWN"
    echo "Unknown type of data : $type"
    exit
fi

#MON_DIR=$5

#STAGE=$6

#log=`ls -1 ${FULL_PATH}/oa_*_*_${run}-${subrun_label}*.log`
#if [ $? != 0 ]; then
#    echo "Log file not found: exit on error " 
#    exit
#fi
###echo " "


if [ -f $log ]; then
    
#CALIBRATION stage
    STAGE=CALIBRATION
    
    OACALIB="0"
    fgrep -Hr "oaCalibMC Job Completed Successfully" $log >/dev/null 2>&1 && OACALIB="1"
    OACALIBTIME=`fgrep 'Run time for oaCalibMC is' $log | awk '{ print $7}' | sed 's/\..*//'`
    if [[ $OACALIB != 0 ]]; then 
		# The following parses out like:
                # 
                # Total Events Read: 37
                # Total Events Written: 37
		# Total Events Read: 37
		# Total Events Written: 37
		# oaCalibMC Job Completed Successfully
		# Total Events Read: 37
		# Total Events Written: 37
		# oaRecon Job Completed Successfully
		# Total Events Read: 37
		# Total Events Written: 0
		# oaAnalysis Job Completed Successfully

	OACALIB_READ=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '3p' | awk '{print $4}'`
	OACALIB_WRITTEN=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '4p' | awk '{print $4}'`
    else
	OACALIB="0"
	OACALIB_READ="0"
	OACALIB_WRITTEN="0"
	OACALIBTIME="0"
    fi
    OUTPUT="${OACALIB} ${OACALIBTIME} ${OACALIB_READ} ${OACALIB_WRITTEN}"

    if [ $SUBJOB_FOR_REAL -eq 1 ]; then
	curl -k --header "Accept: text/plain" --data-binary "$OUTPUT" -X POST "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE" > /dev/null
    else
	echo curl -k --header \"Accept: text/plain\" --data-binary \"$OUTPUT\" -X POST \"https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE\" 
    fi


# RECONSTRUCTION stage
    
    STAGE=RECONSTRUCTION
    
    OARECON="0"
    fgrep -Hr "oaRecon Job Completed Successfully" $log >/dev/null 2>&1 && OARECON="1"
    OARECONTIME=`fgrep 'Run time for oaRecon is' $log | awk '{ print $7}' | sed 's/\..*//'`
    if [[ $OARECON != 0 ]]; then
	
	OARECON_READ=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '6p' | awk '{print $4}'`
	OARECON_WRITTEN=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '7p' | awk '{print $4}'`
    else
	OARECON="0"
	OARECON_READ="0"
	OARECON_WRITTEN="0"
	OARECONTIME="0"
    fi
    OUTPUT="${OARECON} ${OARECONTIME} ${OARECON_READ} ${OARECON_WRITTEN}"

    if [ $SUBJOB_FOR_REAL -eq 1 ]; then
        curl -k --header "Accept: text/plain" --data-binary "$OUTPUT" -X POST "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE" > /dev/null
    else
        echo curl -k --header \"Accept: text/plain\" --data-binary \"$OUTPUT\" -X POST \"https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE\" 
    fi
    

#ANALYSIS stage
    
    STAGE=ANALYSIS

    OAANALYSIS="0"
    fgrep -Hr "oaAnalysis Job Completed Successfully" $log >/dev/null 2>&1 && OAANALYSIS="1"
    OAANALYSISTIME=`fgrep 'Run time for oaAnalysis is' $log | awk '{ print $7}' | sed 's/\..*//'`
    if [[ $OAANALYSIS != 0 ]]; then
	
	OAANALYSIS_READ=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '9p' | awk '{print $4}' || echo 0`
	OAANALYSIS_WRITTEN=`egrep 'Total Events|oaCalibMC Job Comp|oaRecon Job Comp|oaAnalysis Job Comp' $log | sed -n '10p' | awk '{print $4}'`
    else
	OAANALYSIS="0"
	OAANALYSIS_READ="0"
	OAANALYSIS_WRITTEN="0"
	OAANALYSISTIME="0"
    fi
    OUTPUT="${OAANALYSIS} ${OAANALYSISTIME} ${OAANALYSIS_READ} ${OAANALYSIS_WRITTEN}"
    
    if [ $SUBJOB_FOR_REAL -eq 1 ]; then
        curl -k --header "Accept: text/plain" --data-binary "$OUTPUT" -X POST "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE" > /dev/null
    else
        echo curl -k --header \"Accept: text/plain\" --data-binary \"$OUTPUT\" -X POST \"https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/$MON_DIR?${run}/${subrun}/$TYPE/$STAGE\" 
    fi
  
else

    echo "No log found in: ${MON_DIR}/${run}/${subrun}"
    
fi


}
