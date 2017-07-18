#!/bin/bash

#############################################################################
#
# Title: SciNet Catalogue File Registration Script
#
# Usage: Call this script in a specific sample directory:
#        ./cat_cp.sh <run start> <subrun start> <run end> <subrun end> <module step> 
#        where <module step>=(all g4mc elmc cali reco anal logf) and 
#        all=(cali reco anal logf) 
#        
#        It will register files to the T2K File Catalogue Query as viewed
#        here: http://www.hep.lancs.ac.uk/bertram/T2KFileCatalogue.html
#
#############################################################################
        

# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: ./cat_cp.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND"
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


source ${ND280SOFT_DIR}/setup_t2knd280.sh
source ${RUNND280_SETUP}

LOG_DIR=grid_logs
mkdir -p ${LOG_DIR}

get_mc_details


set_run_numbers
set_comment


# Log file for storing catalogue registration output
CAT_LOGFILE=${HERE}/${LOG_DIR}/cat_log.txt
if [ -e $CAT_LOGFILE ]; then
    rm ${CAT_LOGFILE}
fi

# Error file for output of chkLogs.sh which searches for 
# files that failed processing. This file is then used as
# input to grid_cp.sh to skip attempts to copy incomplete 
# files to the GRID.
ERR_FILE=${HERE}/errfile_$RUNSTART-$RUNEND.txt

# Number of runs to copy in parallel 
# (Set negative to disable)
nRunsToCopy=-1
iRun=0

for (( run=$RUNSTART; run<=$RUNEND; run++ ))
do
 
    if [ ! -d ${run} ]; then
	echo "Error: Run directory ${run} does not exist. Did you specify the correct run range?"
	exit 1
    fi
  
    cd $run
      (  
	for (( subrun=0; subrun<=99; subrun=$[$subrun+$nIntFileCombine] ))
	  do
	    
	    if [ ! -d ${subrun} ]; then
		echo "Error: Run/Subrun directory ${run}/${subrun} does not exist. Did you specify the correct subruns?"
		exit 1
	    fi
	    
	    cd $subrun
	    
	    echo "`pwd`/ storeND280FileCatalogue . d " >> $CAT_LOGFILE
	    
	    if [ ${SUBJOB_FOR_REAL} -eq 1 ]; then
		storeND280FileCatalogue . d >> $CAT_LOGFILE
	    fi

	    echo "" >> $CAT_LOGFILE

	    cd ..
	    
	done
      )&

      cd ..

      echo "Registering catalogues for run $run"
      
      let iRun=$(($iRun+1))
      if [ $iRun == $nRunsToCopy ]; then
	  echo "Waiting for run $run...."
	  iRun=0
	  wait
      fi

done # run

