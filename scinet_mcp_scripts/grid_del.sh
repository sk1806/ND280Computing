#!/bin/bash
#


# Do not run anywhere except datamover1 node
if [ "$HOSTNAME" != "gpc-logindm01" ]; then
    echo "Error: Do not run on this node. Do ssh datamover1 first!"
    exit
else
    source /scinet/lcg/grid/userinterface/gLite/etc/profile.d/grid_env.sh
    export LFC_HOST=lfc.gridpp.rl.ac.uk
fi

# Check run number and ND280 module 'step' arguments 
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" || "$5" == "" ]]; then
    echo "Usage: ./grid_cp.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND STEP <Optional: cat (to register catalogues)>"
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



# Directory for storing the GRID transfer command logs
# (useful for debugging this script)
LOG_DIR=${HERE}/grid_ls

echo "Running GRID transfer script for..."
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

# If you specified to copy all steps, then copy 
# all files, skipping redundant g4mc and elmc types:
if [ ${STEPS[0]} == "all" ]; then
    STEPS=(anal cali reco logf)
fi

# Error: You must specify a step or all to copy
if [ $STEPS[0] == "" ]; then
    echo "Must specify STEP"
    exit
fi


set_run_numbers
set_comment


for STEP in "${STEPS[@]}"
do
        
    LIST_FILE=${LOG_DIR}/${STEP}_ls_${RUNSTART}_${RUNEND}.txt
    
    FILES=(`cat $LIST_FILE`)

	
      # Add "verify/nd280vers" to the GRID sample directory for verification files
    if [[ $VERIFY -eq 1 ]]; then
	MON_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
	SAMPLE_DIR=${MON_DIR}/${STEP}
	
      # Final production files
    else
	MON_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
	SAMPLE_DIR=${MON_DIR}/${STEP}
    fi	
    
    for datafile in ${FILES[@]}
    do

	DEL_COMMAND="lcg-del -a lfn:/${LFN}/${SAMPLE_DIR}/${datafile}"

	echo $DEL_COMMAND
    done
    
done # run
