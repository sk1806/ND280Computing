#!/bin/bash
#
#############################################################################
#
# Title: SciNet Local Purging Script
#
# Usage: Make sure you first run grid_ls.sh on Silo and the GRID to produce
#        the list of files present on the remote server. 
#        Then call this script in a specific sample directory:
#        ./purge.sh <run start> <subrun start> <run end> <subrun end> <optional: module step> 
#        where <module step>=(g4mc elmc cali reco anal logf cata cnfg) if you 
#        only want to check existence of a specific stage on the GRID/Silo. E.g.
#        MCP4C.
#
#        g4mc and elmc files are all deleted automatically at the very end.
#
#        Warning: This script does not check if catalogue files have been 
#        succesfully uploaded to the T2K File Catalogue database:
#        http://www.hep.lancs.ac.uk/bertram/T2KFileCatalogue.html
#                 
#
#############################################################################


# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: ./grid_cp.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND <Optional: STEP>"
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



# Directories for storing the grid_ls.sh outputs
GRID_LOG_DIR=${HERE}/grid_ls
SILO_LOG_DIR=${HERE}/silo_ls


echo "Running SciNet purging script for..."
get_mc_details

# If we're in the nd280 chain directory then grab
# the actual specified module step
if [ "${STEP}" == "nd280" ]; then
    STEPS=($5)
elif [ "${STEP}" == "numc" ]; then
    STEPS=(numc) #(gnmc)
else
    echo "Unknown step: " ${STEP}
    exit 1
fi

# Stages to check for
if [[ ${STEPS[0]} == "all" ||  ${STEPS[0]} == "" ]]; then
    STEPS=(anal cali) # Do not purge reco for now until Respin C is done
fi


set_run_numbers
set_comment


for (( run=$RUNSTART; run<=$RUNEND; run++ ))
do

    if [ ! -d ${run} ]; then
	echo "Error: Run directory ${run} does not exist. Did you specify the correct run range?"
	exit 1
    fi

    cd $run

    
    # Check for all input and output lists before the actual
    # transfer loop below, which transfers steps in parallel 
    # background processes.
    for STEP in "${STEPS[@]}"
      do

      # Check for file that is outputted by grid_ls.sh which 
      # checks the GRID for each run/subrun file of each step.
      # This file contains ones that are missing       
	GRID_MISSFILE=${GRID_LOG_DIR}/${STEP}_missing_${RUNSTART}_${RUNEND}.txt
	if [ ! -e ${GRID_MISSFILE} ]; then
	    echo "Can't sub missing files without ${GRID_MISSFILE}"
	    exit 1
	fi
	
	SILO_MISSFILE=${SILO_LOG_DIR}/${STEP}_missing_${RUNSTART}_${RUNEND}.txt
	if [ ! -e ${SILO_MISSFILE} ]; then
	    echo "Can't sub missing files without ${SILO_MISSFILE}"
	    exit 1
	fi

	for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
	do
	    
	    FULL_PATH=${HERE}/${run}/${subrun}
	    
	    if [ ! -d ${FULL_PATH} ]; then
		echo "Error: Run/Subrun directory ${run}/${subrun} does not exist. Did you specify the correct subruns?"
		exit 1
	    fi
	    
	    subrun_label=`printf "%04d" ${subrun}`
	    
            # Files that do not exist on the GRID
	    FILE_MISSING=`grep "${run}-${subrun_label}" ${GRID_MISSFILE}`
	    if [[ "${FILE_MISSING}" == "${run}-${subrun_label}" ]]; then
                echo ${FILE_MISSING} ${STEP} not on GRID, will not purge
		continue
	    fi
	    	    
            # Files that do not exist on Silo
	    FILE_MISSING=`grep "${run}-${subrun_label}" ${SILO_MISSFILE}`
	    if [[ "${FILE_MISSING}" == "${run}-${subrun_label}" ]]; then
                echo ${FILE_MISSING} ${STEP} not on Silo, will not purge
		continue
	    fi

	    cd $subrun
	    
            # List the file
	    FILETOFIND=oa_*_${run}-${subrun_label}_*_${STEP}_*_${COMMENT}*.root
	    datafile=`ls -1 oa_*_${run}-${subrun_label}_*_${STEP}_*_${COMMENT}*.root`

	    if [ $SUBJOB_FOR_REAL -eq 1 ]; then
		echo "Real: rm ${datafile}"
		rm ${datafile} &
	    else
		echo "Fake: rm ${datafile}"
	    fi
		
	    cd ..

	done # subrun

    done # STEP

    # Remove all g4mc, elmc files
    echo 
    echo "Removing ALL g4mc and elmc files..."
    if [ $SUBJOB_FOR_REAL -eq 1 ]; then
        echo "Real: rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_g4mc_*_${COMMENT}*.root"
        echo "Real: rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_elmc_*_${COMMENT}*.root"
        rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_g4mc_*_${COMMENT}*.root
        rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_elmc_*_${COMMENT}*.root
    else
        echo "Fake: rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_g4mc_*_${COMMENT}*.root"
        echo "Fake: rm ${HERE}/${run}/*/oa_*_${run}-${subrun_label}_*_elmc_*_${COMMENT}*.root"
    fi


    cd ..
    
done # run
