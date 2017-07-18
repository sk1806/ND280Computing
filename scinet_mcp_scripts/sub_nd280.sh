#!/bin/bash 
#
#############################################################################
#
# Title: SciNet ND280 software chain job submission script
#
# Usage: This script should be called from the specific sample directory
#        ./sub_nd280.sh <Run start> <Subrun start> <Run end> <Subrun end> <Module start> <Module end>
#        where the subrun ranage applies to each run.
#
#        <Module start/end> are optional arguments which specifies the start/ending 
#        module in the ND280 chain, searching in the specified run/subrun directory 
#        for the appropriate input file from the previous step. Options are:
#        (oaCherryPicker nd280MC elecSim oaCalibMC oaRecon oaAnalysis). If these 
#        are not specified, then the full chain is run. If <Module start> is 
#        specified but not <Module end> then the full chain following <Module start> 
#        is run (see set_modules() in sub_header.sh for more details).
# 
#############################################################################



# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh


# Check run number arguments
if [[ "$1" == "" || "$2" == "" || "$3" == "" || "$4" == "" ]]; then
    echo "Usage: ./sub_nd280.sh RUNSTART SUBRUNSTART RUNEND SUBRUNEND"
    exit 1
fi

# Get ND280 module to resume processing with
MODULE_START=$5
MODULE_END=$6

# MC run number starts with 9 and is 8 digits
RUNSTART=9`printf "%07d" $1`
  RUNEND=9`printf "%07d" $3`

SUBRUNSTART=$2
  SUBRUNEND=$4


. ${PRODUCTION_DIR}/sub_header.sh



# Function to find the input 'numc' file (taking care of the hash value)
# and combining files if necessary for cherry picking
function mk_input_numc_file {

    run_numc=$run

    # See function set_run_numbers() in sub_header.sh to define number of combined files
    for (( iFile=0; iFile<nIntFileCombine; iFile++ ))
      do
      
      # Initialize the iFile'th entry in the input file list
      INPUTFILE[$iFile]=0

      # Subrun number of the current 'numc' file to be combined
      subrun_numc=$[$subrun+$iFile]

      # Store the file list of the input 'numc' directory
      file_list=(`ls ${NUMC_DIR}/${run_numc}/${subrun_numc}`)

      # Loop over all files in the 'numc' directory
      for file_name in "${file_list[@]}"
	do

	# Search for the 'numc' file and add it to the input file list
	if [[ $file_name == oa_*_*_${run_numc}-`printf "%04d" ${subrun_numc}`_*_numc_*_${COMMENT}.root ]]; then
	    INPUTFILE[$iFile]=$file_name
	fi
	
      done 
      
      # Error if a 'numc' file does not exist
      if [[ ${INPUTFILE[$iFile]} == 0 ]]; then
	  echo "Error: ${NUMC_DIR}/${run_numc}/${subrun_numc}/oa_*_*_${run_numc}-`printf "%04d" ${subrun_numc}`_*_numc_*_${COMMENT}.root does not exist" 2>&1 | tee -a ${MISSED_NUMC_FILE}
	  
	  # Exit assuming that the 'numc' generation was perfect
	  #exit

          continue
      fi

      # This is only valid when nIntFileCombine=1 for non-cherry picked files.
      # For cherry picking, the input file is copied to the working directory 
      # and passthrough assumed to be that working directory.
      PASS_THROUGH_DIR=${NUMC_DIR}/${run_numc}/${subrun_numc}

      # Prepend the iFile'th file with it's absolute directory
      INPUTFILE[$iFile]=${PASS_THROUGH_DIR}/${INPUTFILE[$iFile]}

    done
}



function mk_input_nd280_file {

    iInFile=0
    iOutFile=0
  
    # Change this to where you want to read your ND280 input file from
    ND280_INPUT_BASE_DIR=${PRODUCTION_DIR}/B/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}/nd280
    ND280_INPUT_DIR=${ND280_INPUT_BASE_DIR}/${run}/${subrun}

    # Check if there were any processing errors in the desired input file
    # Error file for output of chkLogs.sh which searches for 
    ERR_FILE=${ND280_INPUT_BASE_DIR}/errfile_$RUNSTART-$RUNEND.txt

    # Check for ${ERR_FILE} that contains list of run/subruns with processing error
    chk_err_file

    # Check for failed processes in list
    if [ -e "${ERR_FILE}" ]; then
	FILE_SKIP=`grep "${run} ${subrun_label}" ${ERR_FILE} | egrep "${ALL_MODULES[$[${i_module_start}-1]]}|No log"`
        if [ "${FILE_SKIP}" != "" ]; then
	    echo "Error in input ${ALL_MODULES[$[${i_module_start}-1]]} file processing"
	    return
	fi
    fi

    # Store the file list of the current directory
    file_list=(`ls ${ND280_INPUT_DIR}`)
    
    # Loop over all files in the directory
    for file_name in "${file_list[@]}"
      do
      
      # Search for any existing output file and add it to the output file list
      if [[ $file_name == oa_*_*_${run}-${subrun_label}_*_${MODULE_FILE[${i_module_start}]}_*_${COMMENT}.root ]]; then
	  OUTPUTFILE[$iOutFile]=$file_name
	  let iOutFile=${iOutFile}+1
      fi

      # Search for the appropriate input file
      if [[ $file_name == oa_*_*_${run}-${subrun_label}_*_${MODULE_FILE[$[${i_module_start}-1]]}_*_${COMMENT}.root ]]; then
	  INPUTFILE[$iInFile]=$file_name
	  let iInFile=${iInFile}+1
      fi
	
    done

    # Error: No input file found
    if  [ ${iInFile} -eq 0 ]; then
	echo Error: ${ND280_INPUT_DIR}/oa_*_*_${run}-${subrun_label}_*_${MODULE_FILE[$[${i_module_start}-1]]}_*_${COMMENT}.root not found
	#exit

    # Make sure there's only one input file in the directory
    elif [[ ${iInFile} > 1 ]]; then
	echo More than 1 possible input file found: 
	for infile in ${INPUTFILE[@]}
	  do
	  echo ${infile}
	done
	echo Please clean up your directories.
	exit

    elif [[ ${iInFile} == 1 ]]; then

	INPUTFILE[0]=${ND280_INPUT_DIR}/${INPUTFILE[0]}
    fi
      
    # Clean up existing output files
    if [[ ${iOutFile} > 0 ]]; then
	
	for outfile in ${OUTPUTFILE[@]}
	  do
	  	  
	  echo 
	  # Real job submission will try to remove existing output files
	  if [ ${SUBJOB_FOR_REAL} -eq 1 ]; then
	      echo "Delete existing output file: ${outfile}?"
	      select yn in "Yes" "No"; do
		  case $yn in
		      Yes ) rm ${HERE}/${run}/${subrun}/${outfile}; break;;
		      No ) echo "Warning: You will have multiple outfiles in the directory."; break;;
		  esac
	      done
	  else
	      echo "Fake submission found existing output file: ${outfile}"
          fi
        done
    fi  

    # This is only valid when nIntFileCombine=1 for non-cherry picked files.
    # For cherry picking, the input file is copied to the working directory 
    # and passthrough assumed to be that working directory.
    PASS_THROUGH_DIR=${NUMC_DIR}/${run}/${subrun}
    
}



# Function to determine what kind of input file to grab
function mk_input_file {
    
    # Initialize INPUTFILE 
    INPUTFILE[0]=0

    # Full chain requires a neutrino interaction 'numc' file
    if [[ "${MODULE_START}" == "" ]]; then
	mk_input_numc_file

    # Cherry picking also requires 'numc' file
    elif [[ "${MODULE_START}" == "oaCherryPicker" ]]; then
	mk_input_numc_file

    # ND280 MC with no cherry picking also requires 'numc' file
    elif [[ "${MODULE_START}" == "nd280MC" && ${CHERRY_PICKED}==0 ]]; then
	mk_input_numc_file
	
    # Specific ND280 module requires file from previous module
    else
	mk_input_nd280_file       
	
    fi

}



##############################################################
# MAIN 

WORKDIR=${HERE}

# Directory for job submission scripts
mkdir -p scripts

# Directory for PBS job output files
mkdir -p spool

# File to store any missing numc file(s)
MISSED_NUMC_FILE=${HERE}/missing_numc.txt

# Get MC details from path
get_mc_details

set_modules
set_run_numbers
set_comment
set_walltime

set_numc_dir

if [[ $VERIFY -eq 1 ]]; then
    MON_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}

# Final production files
else
    MON_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}

fi

# Check for list of missing/failed files when submitting in this mode
if [ $SUBMISS -eq 1 ]; then
    MISSFILE=${HERE}/errfile_${RUNSTART}-${RUNEND}.txt
    if [ ! -e ${MISSFILE} ]; then
        echo "Can't sub missing files without ${MISSFILE}"
        exit 1
    fi
fi

# Batch/node counter for labeling jobs
BATCH=${BATCHIN}

# Counter for number of processes per node
PROCS=0

for (( run=${RUNSTART}; run<=${RUNEND}; run++ ))
  do
  
  # Increment by ${nIntFileCombine} when combining 'numc' files for cherry picking
  for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[${subrun}+${nIntFileCombine}] ))
    do
    
    subrun_label=`printf "%04d" ${subrun}`

    # Function to redo failed or missing subruns 
    if [ $SUBMISS -eq 1 ]; then

	FILE_MISSING=`grep "${run} ${subrun_label}" ${MISSFILE}`

	if [[ "${FILE_MISSING}" != "${run} ${subrun_label}"* ]]; then

            #if [ $subrun == ${SUBRUNEND} ]; then
            #    echo $subrun
            #    sub_unfilled_job
            #fi

	    continue
	fi
	
	# WARNING this clears the current run/subrun directory
	if [ $SUBJOB_FOR_REAL -eq 1 ]; then
            echo "REAL rm -r ${HERE}/${run}/${subrun}"
	    rm -r ${HERE}/${run}/${subrun}
        else
            echo "FAKE rm -r ${HERE}/${run}/${subrun}"            
	fi

    fi

    mkdir -p ${run}/$subrun

    mk_input_file
    if [ ${INPUTFILE[0]} == 0 ]; then
	echo "Skipping run/subrun: ${run}/$subrun"
        continue
    fi

    # Set the path of the original .cfg file and where it should be copied
    set_cfg_filename 
    CFG_FILE_ORIG=${PRODUCTION_DIR}/${CFG_PREFIX}.cfg
    CFG_FILE_PATH=${HERE}/${run}/${subrun}/${CFG_FILE}
     
    #if [ $SUBJOB_FOR_REAL -eq 1 ]; then
        mk_cfg
    #fi
    
    # Set path of job submission script
    SUBFILE=${HERE}/scripts/${CFG_PREFIX}.${MC_TYPE}.${run:0:5}.${BATCH}.sh
    mk_subfile_header

# Set of commands that run on a single processor per node
# There should be at most NPROCS of these per job submission script      
cat >> ${SUBFILE}<<EOF
(
cd ${HERE}/${run}/$subrun
runND280 -c ${CFG_FILE_PATH} >& /dev/null

ssh datamover1 "export PATH=${PRODUCTION_DIR}:\${PATH}; ${PRODUCTION_DIR}/./send_mon_info.pl ${run} ${subrun_label} MCP ${HERE}/${run}/$subrun ${MON_DIR} > /dev/null"
)&

EOF
    let PROCS=$PROCS+1
      
    if [ $PROCS -eq "${NPROCS}" ]; then

cat >> ${SUBFILE}<<EOF
wait

EOF

      # The moment of truth
      sub_job
    fi
      
  done
done

sub_unfilled_job
