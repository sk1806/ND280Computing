#!/bin/bash
#
#############################################################################
#
# Title: SciNet GRID File Listing Script
#
# Usage: This script runs lfc-ls (lcg-ls still needs to be implemented) 
#        using the current sample directory and pipes the output to the file
#        ${LOG_DIR}/lfc_ls_${STEP}.txt. Note that there are no run/subrun 
#        directories on the GRID and the entire contents of a sample/step 
#        are returned.
#
#        Subruns missing on the LFC are reported in the file:
#        ${LOG_DIR}/lfc_ls_missing_${STEP}.txt
#
#        All of the above can also be done on Silo using gsissh by specifying
#        "silo" as the 6th argument (default is GRID)
#
#        To check filesizes, specify "filesize" as the 7th argument. (Then 
#        you need to specify either "grid" or "silo" as the 6th.) 
#        Warning: Assumes only 1 file of each stage in run/subrun directory.
#
#############################################################################

# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" || "$5" == "" ]]; then
    echo "Usage: ./grid_ls.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND STEPS <Optional: silo>"
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

get_mc_details

STEPS=($5)

# If you specified to copy all steps, then copy 
# all files, skipping redundant g4mc and elmc types:
if [[ ${STEPS[0]} == "all" ]]; then

    if [ ${STEP} == "nd280" ]; then
        if [ "$CHERRY_PICKED" == 0 ]; then
            STEPS=(anal cali reco logf)
        else
            STEPS=(anal cali reco nucp logf)
        fi

    elif [[ ${STEP} == "numc" ]]; then

        if [ $SIMNAME == "genie" ]; then
            STEPS=(numc gnmc)
        elif [ $SIMNAME == "neut" ]; then
            STEPS=(numc)
        fi

    fi
fi

# Error: You must specify a step or all to copy
if [ $STEPS[0] == "" ]; then
    echo "Must specify STEP"
    exit
fi

set_run_numbers
set_comment

SITE=$6

if [ "${SITE}" == "" ]; then
    echo "Warning: grid or silo site not specified. Using 'lfc-ls' on T2K GRID LFC"
    SITE="grid"
fi

CHKFILESIZE=0
if [ "$7" == "filesize" ]; then
    CHKFILESIZE=1
    echo "Checking file sizes"
fi

FLAGS=""
if [ $CHKFILESIZE -eq 1]; then
    FLAGS="-l"
fi

if [ $SITE == "grid" ]; then
    LS_COMMAND="lfc-ls ${FLAGS}"
    REM_DIR="/${LFN}"
    LOG_DIR=grid_ls
elif [ $SITE == "silo" ]; then
    LS_COMMAND="gsissh t2k@silo.westgrid.ca ls ${FLAGS}"
    REM_DIR="/home/t2k/data"
    LOG_DIR=silo_ls 
fi

mkdir -p $LOG_DIR

for STEP in "${STEPS[@]}"
  do

    MISSED_FILE=${HERE}/${LOG_DIR}/${STEP}_missing_${RUNSTART}_${RUNEND}.txt
    if [ -e $MISSED_FILE ]; then
	rm $MISSED_FILE
    fi
    touch $MISSED_FILE
    
    LIST_FILE=${HERE}/${LOG_DIR}/${STEP}_ls_${RUNSTART}_${RUNEND}.txt
    if [ -e $LIST_FILE ]; then
	rm $LIST_FILE
    fi

    # Add "verify/nd280vers" to the GRID sample directory for verification files
    if [[ $VERIFY -eq 1 ]]; then
	SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}/${STEP}
	
    # Final production files
    else
	SAMPLE_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}/${STEP}
    fi
    
    echo "${LS_COMMAND} ${REM_DIR}/${SAMPLE_DIR} 2>&1 | tee -a ${LIST_FILE}"
    
    DATAFILES=(`${LS_COMMAND} ${REM_DIR}/${SAMPLE_DIR} 2>&1 | tee -a ${LIST_FILE}`)
    
    if [[ "${STEP}" == "logf" && "${SITE}" == "grid" ]]; then
	continue
    fi
    
    for (( run=$RUNSTART; run<=$RUNEND; run++ ))
    do
	
	nMiss=0
	
	for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
	do
	    
	    subrun_label=`printf "%04d" ${subrun}`
	    
	    FILETOFIND=oa_*_${run}-${subrun_label}_*_${STEP}_*_${COMMENT}*.root
	    
	    LISTEDFILE=`ls ${FLAGS} ${HERE}/${run}/${subrun}/${FILETOFIND}`
	    
	    if [ $CHKFILESIZE -eq 0 ]; then
		FILEBASENAME=`basename ${LISTEDFILE}`
		
	    else
		FILE_ATTRIBUTES=(`echo "${LISTEDFILE}" | awk '{
   		    n = split ( $0, a, " " )
   		    for ( i = 1; i <= n; i++ ) {     
      			printf( "%s\n", a[ i ] );
   		    }
		    }'`)

		FILEBASENAME=`basename ${FILE_ATTRIBUTES[7]}`
		FILESIZE=`${FILE_ATTRIBUTES[4]}`
	    fi


	    FILE_MISSING="${run}-${subrun_label}"
	    FILE_FOUND=`grep "${FILEBASENAME}" ${LIST_FILE}`
	    
	    if [ "${FILE_FOUND}" == "" ]; then
		echo "${FILE_MISSING}" 2>&1 | tee -a ${MISSED_FILE}
		let nMiss=$(( $nMiss + 1 ))
	    fi
	    
	done
	
	echo $nMiss $STEP files missing in run $run
	
    done
    
    echo
    
done
