#!/bin/bash
#
#############################################################################
#
# Title: SciNet NEUT/GENIE 'numc' vector generation job submission script
#
# Usage: This script should be called from the specific sample directory
#        ./sub_numc.sh <Run start> <Subrun start> <Run end> <Subrun end>
#        where the subrun ranage applies to each run.
#
# Since all processes use a common flux file and the process time is 
# relatively short (<30 minutes), this script bundles all the specified 
# subruns of a single run into one node, running 8 subruns on all 8 
# processors until they all finish, after which it continues to the next
# 8 subruns.
#
#############################################################################


# Check run number arguments
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: ./sub_numc.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND"
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


####### MAIN #######

# This is the directory where flux files will be copied to and 
# program output will happen (for interaction vector generation, 
# this can be /dev/shm, the local RAM disk on each node).
WORKDIR=${SCRDIR}

# Directory for job submission scripts
mkdir -p scripts

# Directory for PBS job output files
mkdir -p spool

# Get MC details from path
get_mc_details

if [ ${STEP} != "numc" ]; then
    echo "Error: Call only for numc generation"
    exit
fi

set_run_numbers
set_pot
set_comment
set_walltime

set_numc_dir

# Batch/node counter for labeling jobs
BATCH=${BATCHIN}

PROCS=0

for (( run=${RUNSTART}; run<=${RUNEND}; run++ ))
  do
  
  for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun++ ))
    do
    
    mkdir -p ${run}/${subrun}
    
    # Set the path of the original .cfg file and where it should be copied
    set_cfg_filename 
    CFG_FILE_ORIG=${PRODUCTION_DIR}/${CFG_PREFIX}.cfg
    CFG_FILE_PATH=${HERE}/${run}/${subrun}/${CFG_FILE}
    
    mk_cfg
    
  done
    
  # For subrun looping within a job submission script
  CFG_FILE_PATH_SUB="${HERE}/${run}/\${subrun}/${CFG_FILE_SUB}"
  
  # Set path of job script
  SUBFILE=${HERE}/scripts/${CFG_PREFIX}.${COMMENT}.${BATCH}.sh
  mk_subfile_header

# Set of commands that run on a single processor per node
# There should be at most NPROCS(=8) of these per job submission script
cat >> ${SUBFILE}<<EOF

# Processors per node counter
PROCS=0

for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun++ ))
  do 
    
  (
  mkdir -p ${MC_NAME}_${RESPIN}_mcp_${SIMNAME}_${BASELINE}_${vol}_${MC_TYPE}_${STEP}_${run}_\${subrun}
  cd ${MC_NAME}_${RESPIN}_mcp_${SIMNAME}_${BASELINE}_${vol}_${MC_TYPE}_${STEP}_${run}_\${subrun}

  ln -sf ${WORKDIR}/${FLUX_FILENAMES[$idetid]}.root . 
  ln -sf ${WORKDIR}/${MAXINT_FILE} .

  runND280 -c ${CFG_FILE_PATH_SUB} >& /dev/null
EOF

  if [ $SIMNAME == neut ]; then
cat >> ${SUBFILE}<<EOF

  rm oa_*.geo.root
EOF
  fi

cat >> ${SUBFILE}<<EOF
  mv oa_* ${HERE}/${run}/\${subrun}/.

  cd ../
  rm -rf ${MC_NAME}_${RESPIN}_mcp_${SIMNAME}_${BASELINE}_${vol}_${MC_TYPE}_${STEP}_${run}_\${subrun}
  )&

  let PROCS=\${PROCS}+1

  # Finish once we've added the desired number of processes per node  
  if [ \${PROCS} -eq $NPROCS ]; then
    PROCS=0
    wait
  fi

done

wait

EOF
        
  # The moment of truth
  sub_job

done

sub_unfilled_job
