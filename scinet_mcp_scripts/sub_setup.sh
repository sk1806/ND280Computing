#!/bin/bash
#
#############################################################################
#
# Title: SciNet NEUT/GENIE setup job submission script
#
# Usage: This script should be called from the root production directory
#        ./sub_setup.sh <no arguments>
#        where you set the desired baselines and volumes to generate 
#        setup files for in the arrays below. Ensure that the flux inputs
#        are properly set in sub_header.sh and that you have created the 
#        directory structure using mk_dir.sh
#
#############################################################################


# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh

echo ""

####### MAIN #######

# This is the directory where flux files will be copied to and 
# program output will happen (for generator setup, this can be 
# /dev/shm, the local RAM disk on each node).
WORKDIR=${SCRDIR}

# Directory for job submission scripts
mkdir -p scripts

# Directory for PBS job output files
mkdir -p spool

# Batch/node counter for labeling jobs
BATCH=${BATCHIN}

# Processors per node counter
PROCS=0

# For filenaming
run=0
subrun=0


# Loop over all samples since we need to create a setup
# file for each specific geometry
for RESPIN in ${RESPINS[@]}
  do
  
  for VOLUME in ${VOLUMES[@]}
    do
    
    for SIMNAME in ${SIMNAMES[@]}
      do
      
      for BASELINE in ${BASELINES[@]}
	do
	
	for MC_TYPE in ${MC_TYPES[@]}
	  do
	  
	  for STEP in ${STEPS[@]}
	    do
	    
	      
	    if [[ $VERIFY -eq 1 ]]; then
		NUMC_DIR=${PRODUCTION_DIR}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${VOLUME}/${MC_TYPE}/${STEP}
	    else
		NUMC_DIR=${PRODUCTION_DIR}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${VOLUME}/${MC_TYPE}/${STEP}
	    fi

            dir=${NUMC_DIR}/setup
             
	    # Warning: This assumes that you have generated the only the desired samples correctly
	    #          in mk_dir.sh
	    if [ ! -d ${dir} ]; then
		continue
	    fi
	    
	    cd ${dir}
            #rm ${dir}/*

	    HERE=`pwd`

	    get_mc_details

	    if [ ${STEP} != "numc" ]; then
		echo "Error: Call only sub_setup.sh for numc generation"
		exit
	    fi
	    
	    set_comment
	    set_walltime

            # Set the path of the original .cfg file and where it should be copied
	    set_cfg_filename
	    CFG_FILE_PATH=${HERE}/${CFG_FILE}
	    CFG_FILE_ORIG=${PRODUCTION_DIR}/${CFG_PREFIX}.cfg
	    
	    mk_cfg
	    
	    # Set path of job submission script
	    SUBFILE=${PRODUCTION_DIR}/scripts/${SIMNAME}_setup.${BATCH}.sh
	    mk_subfile_header

# Set of commands that run on a single processor per node
# There should be at most NPROCS of these per job submission script
cat >> ${SUBFILE}<<EOF
if [ ! -e ${FLUX_FILENAMES[$idetid]}.root ]; then
    cp ${FLUX_FULL_PATH[$idetid]} .
fi

(
mkdir -p ${MC_NAME}_${RESPIN}_mcp_${SIMNAME}_${BASELINE}_${VOLUME}_${MC_TYPE}_${STEP}_setup
cd ${MC_NAME}_${RESPIN}_mcp_${SIMNAME}_${BASELINE}_${VOLUME}_${MC_TYPE}_${STEP}_setup
ln -sf ${WORKDIR}/${FLUX_FILENAMES[$idetid]}.root .
runND280 -c ${CFG_FILE_PATH} >& /dev/null

mv *.log ${HERE}/.
mv ${MAXINT_FILE}* ${HERE}/${MAXINT_FILE}
)&
EOF

            let PROCS=$PROCS+1

            # Finish once we've added the desired number of processes per node
	    if [ $PROCS -eq "${NPROCS}" ]; then

# 'wait' command is necessary for all background processes to finish or else 
# PBS will immediately kill the job
cat >> ${SUBFILE}<<EOF
wait

EOF
                # The moment of truth
                sub_job

	    fi
	

	    
	  done
	done
      done
    done
  done
done

sub_unfilled_job
