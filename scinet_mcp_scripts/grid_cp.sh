#!/bin/bash
#
#############################################################################
#
# Title: SciNet GRID transfer script
#
# Usage: Call this script in a specific sample directory:
#        ./grid_cp.sh <run start> <subrun start> <run end> <subrun end> <module step> <optional: cat>
#        where <module step>=(all g4mc elmc cali reco anal logf cata cnfg) where 
#        all=(cali reco anal logf) and setting 
#        <cat>=cat will register the catalogue files on the T2K file query.
#         
#        Make sure to set the "VERIFY" flag in sub_header.sh in case you are 
#        uploading files to be verified. This will copy the files into the 
#        appropriate "verify/nd280vers" directory on the GRID.
#
#        You should run chkLogs.sh to check the results of each process.
#        If there were errors,a file containing the failed runs/subruns 
#        should be produced: errfile_$RUNSTART-$RUNEND.txt which is then
#        used by this script to skip the incomplete files.
#
#        The script will then copy the specified subruns in each run to the 
#        GRID storage element (SE) specified in grid_header.sh and register 
#        the file on the Logical File Catalogue (LFC).
#
#        Similarly to submitting jobs, you can set the SUBJOB_FOR_REAL 
#        variable in sub_header.sh to 0, to and check the outputs in the 
#        grid_logs directory that contain the actual commands that will 
#        execute.
#                 
#
#############################################################################


# Set number of times you want the script to retry the copy
# (Note it will try to delete any existing copy on the GRID)
nRetries=0

# The GRID copy command
# lcg-cr: copies to SE and registers to LFC
# lcg-cp: copies to SE only (not recommended)
# lcg-rf: registers files already on the SE
CP_COMMAND="lcg-cr"

# Flags for the CP_COMMAND
# -n: number of streams per file
FLAGS="-n 6"

# Available SEs we can copy to
# (See grid_header.sh)
nSites=3
SITES=(ral qmul3 triumf)

# Select SE to copy to.
#  (Note you can also loop through sites if you need more 
#  bandwidth for uploading, but requires some modification 
#  of the script below)
se_ind=2
SITE=${SITES[$se_ind]}

# Number of runs to copy in parallel 
# (Set negative to disable)
nRunsToCopy=-1
iRun=0


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


# Flag to copy catalogue files as outlined here:
# http://www.hep.lancs.ac.uk/nd280Doc/devel/invariant/nd280Control/catalogue.html
if [ "$6" == "cat" ]; then
    REGISTER_CAT=1
    # Load ND280Control for catalogue registration macro
    source ${ND280SOFT_DIR}/setup_t2knd280.sh
    source ${RUNND280_SETUP}
elif [ "$6" == "" ]; then
    REGISTER_CAT=0
else
    echo "Unknown argument for cata file copy flag: $6"
    echo "Did you mean \"cat\"?"
    exit 
fi




# Directory for storing the GRID transfer command logs
# (useful for debugging this script)
LOG_DIR=${HERE}/grid_logs
mkdir -p ${LOG_DIR}

echo "Running GRID transfer script for..."
get_mc_details


# Log file for storing catalogue registration output
CAT_LOGFILE=${LOG_DIR}/cat_log.txt
if [ -e $CAT_LOGFILE ]; then
    rm ${CAT_LOGFILE}
fi


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
    if [ "$CHERRY_PICKED" == 0 ]; then
        STEPS=(anal cali reco logf)
    else
        STEPS=(anal cali reco nucp logf)
    fi
fi

# Error: You must specify a step or all to copy
if [ $STEPS[0] == "" ]; then
    echo "Must specify STEP"
    exit
fi


set_run_numbers
set_comment

set_se


# Error file for output of chkLogs.sh which searches for 
# files that failed processing. This file is then used as
# input to grid_cp.sh to skip attempts to copy incomplete 
# files to the GRID.
ERR_FILE=${HERE}/errfile_$RUNSTART-$RUNEND.txt
#ERR_FILE=${HERE}/errfile_$RUNSTART-$(( $RUNSTART + 1 )).txt

# Check for file that contains list of run/subruns with processing error
chk_err_file


for (( run=$RUNSTART; run<=$RUNEND; run++ ))
do
 
    # Uncomment the following so cycle through SEs
    #SITE=${SITES[$se_ind]}
    #set_se

    #se_ind=$[$se_ind+1]
    #if [ $se_ind -ge $nSites ]; then
    #    se_ind=0
    #fi

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
      # This file contains ones that are missing and will be 
      # used later in this script to select files to copy.
      if [ $SUBMISS -eq 1 ]; then
	  MISSFILE=${HERE}/grid_ls/${STEP}_missing_${RUNSTART}_${RUNEND}.txt
	  if [ ! -e ${MISSFILE} ]; then
	      echo "Can't sub missing files without ${MISSFILE}"
	      exit 1
	  fi
      fi

      # Reset file that stores the log of failed transfers for
      # this call of the script.
      MISSED_FILE=${LOG_DIR}/${STEP}_${run}_miss.txt
      if [ -e $MISSED_FILE ]; then
	  rm $MISSED_FILE
      fi

      # Reset the command log file for this call of the script
      LOG_FILE=${LOG_DIR}/${STEP}_${run}_log.txt
      if [ -e $LOG_FILE ]; then
	  rm $LOG_FILE
      fi

    done



    # Now setup each step; copy if it is a log, cata, cnfg step
    for STEP in "${STEPS[@]}"
      do
	  
      # Add "verify/nd280vers" to the GRID sample directory for verification files
      if [[ $VERIFY -eq 1 ]]; then
	  MON_DIR=${MC_NAME}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
	  SAMPLE_DIR=${MON_DIR}/${STEP}

      # Final production files
      else
	  MON_DIR=${MC_NAME}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${vol}/${MC_TYPE}
	  SAMPLE_DIR=${MON_DIR}/${STEP}
      fi

      # Input and output lists (these should have the same names as 
      # in above STEP loop
      MISSFILE=${HERE}/grid_ls/${STEP}_missing_${RUNSTART}_${RUNEND}.txt
      MISSED_FILE=${LOG_DIR}/${STEP}_${run}_miss.txt
      LOG_FILE=${LOG_DIR}/${STEP}_${run}_log.txt


      # Step dependent setup, if you want to copy specific steps to 
      # different SEs for example, or if you want tar files beforehand
      if [ $STEP == "reco" ]; then
	  SITE=${SITE}  # Command placeholder 

      elif [ $STEP == "cali" ]; then
          SITE=${SITE}  # Command placeholder 

      elif [ $STEP == "anal" ]; then
          SITE=${SITE}  # Command placeholder 

      # Log files are tar'ed and gzipped per run, before uploading
      elif [ $STEP == "logf" ]; then
	  
	  # Name of tarball
          datafile=oa_${MC_TYPE}_${run}_${STEP}_${COMMENT}.tgz
          
	  # tar command including location of new file (in the run directory)
	  FULL_COMMAND="tar -czf ${HERE}/${run}/${datafile} */oa_*_${run}-*_*_${STEP}_*_${COMMENT}.log"
	 
          if [[ ${CP_COMMAND} != "lcg-rf" ]]; then

              echo ${FULL_COMMAND} > $LOG_FILE
  	  
              if [ $SUBJOB_FOR_REAL -eq 1 ]; then
                  ${FULL_COMMAND} >> $LOG_FILE 2>&1
              fi

          # Delete existing file on LFC and SEs                                                            

	      lfc-ls /${LFN}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
	      GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`

	      if [ "${GRID_FILE}" == "" ]; then
		  
		  DEL_COMMAND="lcg-del -a lfn:/${LFN}/${SAMPLE_DIR}/${datafile}"
		  
		  echo ${DEL_COMMAND} >> $LOG_FILE
		  
		  if [ $SUBJOB_FOR_REAL -eq 1 ]; then
		      ${DEL_COMMAND} >> $LOG_FILE 2>&1
		  fi
		  
              # Delete existing file on SE
	      else
		  lcg-ls srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
		  GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`
		  
		  if [ "${GRID_FILE}" == "" ]; then
		      
		      DEL_COMMAND="lcg-del srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
		      
		      echo ${DEL_COMMAND} >> $LOG_FILE
		      
		      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
			  ${DEL_COMMAND} >> $LOG_FILE 2>&1
		      fi		  
		      
		  fi
		  
	      fi
	  fi

	  
	  # The copy commands 
	  if [ ${CP_COMMAND} == "lcg-cr" ]; then
	      FULL_COMMAND="${CP_COMMAND} ${FLAGS} -d srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} file:${HERE}/${run}/${datafile}"
	  elif [ ${CP_COMMAND} == "lcg-cp" ]; then
	      FULL_COMMAND="${CP_COMMAND} ${FLAGS} file:${HERE}/${run}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
	  elif [ ${CP_COMMAND} == "lcg-rf" ]; then
	      FULL_COMMAND="${CP_COMMAND} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
	  fi
	  
          echo ${FULL_COMMAND} >> $LOG_FILE
	      
          if [ $SUBJOB_FOR_REAL -eq 1 ]; then
    	      ${FULL_COMMAND} >> $LOG_FILE 2>&1
	  fi
	  
	  # Do not process subrun loop since we tar'ed them all already
          continue

      # Catalogue files are tar'ed and gzipped per run, before uploading
      elif [ $STEP == "cata" ]; then
	  
	  # Name of tarball
          datafile=oa_${MC_TYPE}_${run}_${STEP}_${COMMENT}.tgz
          
	  # tar command including location of new file (in the run directory)
	  FULL_COMMAND="tar -czf ${HERE}/${run}/${datafile} */oa_*_${run}-*_*_*_*_${COMMENT}_catalogue.dat"
	  
          if [[ ${CP_COMMAND} != "lcg-rf" ]]; then

	      echo ${FULL_COMMAND} > $LOG_FILE
	      
	      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
		  ${FULL_COMMAND} >> $LOG_FILE 2>&1
	      fi
	      
          # Delete existing file on LFC and SEs                                                            
	      
              lfc-ls /${LFN}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
              GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`

              if [ "${GRID_FILE}" == "" ]; then

                  DEL_COMMAND="lcg-del -a lfn:/${LFN}/${SAMPLE_DIR}/${datafile}"

                  echo ${DEL_COMMAND} >> $LOG_FILE

                  if [ $SUBJOB_FOR_REAL -eq 1 ]; then
                      ${DEL_COMMAND} >> $LOG_FILE 2>&1
                  fi

              # Delete existing file on SE                                                                  
              else
                  lcg-ls srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
                  GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`

                  if [ "${GRID_FILE}" == "" ]; then
                        
                      DEL_COMMAND="lcg-del srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
                        
                      echo ${DEL_COMMAND} >> $LOG_FILE
                        
                      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
                          ${DEL_COMMAND} >> $LOG_FILE 2>&1
                      fi                
                        
                  fi

              fi
          fi    
                
	  # The copy commands
	  if [ ${CP_COMMAND} == "lcg-cr" ]; then
	      FULL_COMMAND="${CP_COMMAND} ${FLAGS} -d srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} file:${HERE}/${run}/${datafile}"
	  elif [ ${CP_COMMAND} == "lcg-cp" ]; then
	      FULL_COMMAND="${CP_COMMAND} ${FLAGS} file:${HERE}/${run}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
	  elif [ ${CP_COMMAND} == "lcg-rf" ]; then
	      FULL_COMMAND="${CP_COMMAND} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
	  fi
	  
          echo ${FULL_COMMAND} >> $LOG_FILE
	  
          if [ $SUBJOB_FOR_REAL -eq 1 ]; then
              ${FULL_COMMAND} >> $LOG_FILE 2>&1
          fi
	  
	  # Do not process subrun loop since we tar'ed them all already
          continue

      # CFG files are tar'ed and gzipped per run, before uploading
      elif [ $STEP == "cnfg" ]; then

          # Name of tarball
          datafile=oa_${MC_TYPE}_${run}_${STEP}_${COMMENT}.tgz

          # tar command including location of new file (in the run directory)
          FULL_COMMAND="tar -czf ${HERE}/${run}/${datafile} */*_*_${vol}_${BASELINE}_${run}-*.cfg"

          if [[ ${CP_COMMAND} != "lcg-rf" ]]; then                                                                                                                                                                                                                                 
	      echo ${FULL_COMMAND} > $LOG_FILE
	      
	      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
		  ${FULL_COMMAND} >> $LOG_FILE 2>&1
	      fi
	      
          # Delete existing file on LFC and SEs                                                                                                                                                                                                                                
              lfc-ls /${LFN}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
              GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`

              if [ "${GRID_FILE}" == "" ]; then

                  DEL_COMMAND="lcg-del -a lfn:/${LFN}/${SAMPLE_DIR}/${datafile}"

                  echo ${DEL_COMMAND} >> $LOG_FILE

                  if [ $SUBJOB_FOR_REAL -eq 1 ]; then
                      ${DEL_COMMAND} >> $LOG_FILE 2>&1
                  fi

              # Delete existing file on SE                                                                                                                                                                                                                                     
              else
                  lcg-ls srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} &> ${LOG_DIR}/tmpfile.txt
                  GRID_FILE=`grep "No such file or directory" ${LOG_DIR}/tmpfile.txt`

                  if [ "${GRID_FILE}" == "" ]; then

                      DEL_COMMAND="lcg-del srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"

                      echo ${DEL_COMMAND} >> $LOG_FILE

                      if [ $SUBJOB_FOR_REAL -eq 1 ]; then
                          ${DEL_COMMAND} >> $LOG_FILE 2>&1
                      fi

                  fi

              fi
          fi             
          
          # The copy commands 
          if [ ${CP_COMMAND} == "lcg-cr" ]; then
              FULL_COMMAND="${CP_COMMAND} ${FLAGS} -d srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} file:${HERE}/${run}/${datafile}"
          elif [ ${CP_COMMAND} == "lcg-cp" ]; then
              FULL_COMMAND="${CP_COMMAND} ${FLAGS} file:${HERE}/${run}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
	  elif [ ${CP_COMMAND} == "lcg-rf" ]; then
	      FULL_COMMAND="${CP_COMMAND} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
          fi
          
          echo ${FULL_COMMAND} >> $LOG_FILE

          if [ $SUBJOB_FOR_REAL -eq 1 ]; then
              ${FULL_COMMAND} >> $LOG_FILE 2>&1
          fi

          # Do not process subrun loop since we tar'ed them all already
          continue


      elif [ $STEP == "numc" ]; then
          SITE=${SITE} # Command placeholder 

      elif [ $STEP == "gnmc" ]; then
          SITE=${SITE} # Command placeholder 

      elif [ $STEP == "nucp" ]; then
          SITE=${SITE} # Command placeholder 

      else
          echo "Unknown step = $STEP"  >> $LOG_FILE 2>&1
          exit
      fi


      # Place each step's large copy process in a background process: (...)&
      #(

      for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
	do

	FULL_PATH=${HERE}/${run}/${subrun}

	  if [ ! -d ${FULL_PATH} ]; then
	      echo "Error: Run/Subrun directory ${run}/${subrun} does not exist. Did you specify the correct subruns?"
	      exit 1
	  fi

	subrun_label=`printf "%04d" ${subrun}`

	# Files that failed transferring a previous time
	# Set this SUBMISS flag in sub_header.sh
	if [ $SUBMISS -eq 1 ]; then
	    FILE_MISSING=`grep "${run}-${subrun_label}" ${MISSFILE}`
	    
	    if [[ "${FILE_MISSING}" != "${run}-${subrun_label}" ]]; then
		continue
	    fi
	fi
	
        # Files you want to intentionally skip
	if [ -e "$SKIPFILE" ]; then
	    FILE_SKIP=`grep "${run} ${subrun_label}" ${SKIPFILE}`
	    
	    if [[ "${FILE_SKIP}" == "${run} ${subrun_label}" ]]; then
		continue
	    fi
	fi


	# Check for failed processes in list
	if [ -e "${ERR_FILE}" ]; then
	    FILE_SKIP=`grep "${run} ${subrun_label}" ${ERR_FILE}`
            if [ "${FILE_SKIP}" != "" ]; then
		SKIP_STEP=`echo $FILE_SKIP | cut -d' ' -f6`

		# Skip all files following and including nd280MC module
		if   [ "${SKIP_STEP}" == nd280MC ]; then
                    if [ $STEP == g4mc -o $STEP == elmc -o $STEP == cali -o $STEP == reco -o $STEP == anal ]; then
			echo "Skipping ${run} ${subrun_label} all steps after ${SKIP_STEP}" >> $LOG_FILE

			continue
                    fi
		    
                # Skip all files following and including elecSim module
		elif [ "${SKIP_STEP}" == elecSim ]; then
                    if [ $STEP == elmc -o $STEP == cali -o $STEP == reco -o $STEP == anal ]; then
			echo "Skipping ${run} ${subrun_label} all steps after ${SKIP_STEP}" >> $LOG_FILE

			continue
                    fi

                # Skip all files following and including oaCalibMC module
		elif [ "${SKIP_STEP}" == oaCalibMC ]; then
                    if [ $STEP == cali -o $STEP == reco -o $STEP == anal ]; then
			echo "Skipping ${run} ${subrun_label} all steps after ${SKIP_STEP}" >> $LOG_FILE
			continue
                    fi

                # Skip all files following and including oaRecon module
		elif [ "${SKIP_STEP}" == oaRecon ]; then
                    if [ $STEP == reco -o $STEP == anal ]; then
			echo "Skipping ${run} ${subrun_label} all steps after ${SKIP_STEP}" >> $LOG_FILE
			continue
                    fi

                # Skip oaAnalysis files
		elif [ "${SKIP_STEP}" == oaAnalysis ]; then 
                    if [ $STEP == anal ]; then
		        echo "Skipping ${run} ${subrun_label} all steps after ${SKIP_STEP}" >> $LOG_FILE
                        continue
                    fi
		    
		# No module specified in error file, so skip all steps to be safe
		else
                    if [ $STEP == anal -o $STEP == reco -o $STEP == cali ]; then
			
			echo "Skipping ${run} ${subrun_label} $STEP" >> $LOG_FILE
			
			continue
                    fi
		fi

		# Skip numc if found an error
		if [ $STEP == numc ]; then
		    echo "Skipping ${run} ${subrun_label} $STEP" >> $LOG_FILE
		    continue
		fi

	    fi
	fi

	
	# Finally we can continue with the transfer process

	cd $subrun
	
	# Grab the list of files in the current run/subrun directory
	DATAFILES=(`ls`)
	
	# State of file transfer
	COPIED_FILE=0
	
	for datafile in "${DATAFILES[@]}"
	do
	    # Set the file name to search for (run number and comment should be enough 
	    # to fully specify the file)
	    FILETOFIND=oa_*_${run}-`printf "%04d" ${subrun}`_*_${STEP}_*_${COMMENT}*.root

	    if [[ ${datafile} != ${FILETOFIND} ]]; then
		continue
	    fi
	    
	    echo "" >> $LOG_FILE
	    
	    # Current retry step
	    RETRIES=0
	    
	    # Loop to retry copies
	    while [ $RETRIES -le $nRetries ]
	    do
		
		# The copy commands 
		if [ ${CP_COMMAND} == "lcg-cr" ]; then
		    FULL_COMMAND="${CP_COMMAND} ${FLAGS} -d srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} file:${FULL_PATH}/${datafile}"
		elif [ ${CP_COMMAND} == "lcg-cp" ]; then
		    FULL_COMMAND="${CP_COMMAND} ${FLAGS} file:${FULL_PATH}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
		elif [ ${CP_COMMAND} == "lcg-rf" ]; then
		    FULL_COMMAND="${CP_COMMAND} -l lfn:/${LFN}/${SAMPLE_DIR}/${datafile} srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
		fi
		
		echo ${FULL_COMMAND} >> $LOG_FILE
		
		if [[ $SUBJOB_FOR_REAL -eq 1 ]]; then
		    ${FULL_COMMAND} >> $LOG_FILE 2>&1
		fi
				
		# Check if the last command exitted succesfully
		if [ "$?" -ne "0" ]; then
    
		    if [ $nRetries -gt 0 ]; then
			
		        # If not, try to delete whatever was partially transferred before trying
		        # again. (This is messy, maybe try to implement the synchronization 
		        # scripts in nd280Computing.)
			DEL_COMMAND="lcg-del -l srm://${SE}/${REMOTE_DIR}/${SAMPLE_DIR}/${datafile}"
			echo ${DEL_COMMAND} >> $LOG_FILE 2>&1
			if [ $SUBJOB_FOR_REAL -eq 1 ]; then
			    ${DEL_COMMAND} >> $LOG_FILE 2>&1
			fi
			
                    fi
		    
		    # Increment retry
		    RETRIES=$[$RETRIES+1]
		    echo "Retry $RETRIES" >> $LOG_FILE
		    
		# Successfull command so break out of retry loop
		else
		    break
		fi
		
	    done  # RETRIES 
	    
	    # Pipe failure to log file
	    if [ $RETRIES -gt $nRetries ]; then
		echo "${FULL_PATH}/${datafile} copy failed" >> $LOG_FILE
		break
	    fi

	    COPIED_FILE=1
	done # datafile

	# Pipe more error messages to files
	if [ ${COPIED_FILE} -eq 0 ]; then
	    echo Missed: ${STEP} ${run} ${subrun_label} >> $LOG_FILE
	    echo "${STEP} ${run} ${subrun_label}" >> $MISSED_FILE
	fi
        
	echo ""  >> $LOG_FILE
	
	cd ..
      done # subrun
      
      #)&


    done # STEP

    # Register catalogue files to T2K File Registry using nd280Control macro
    if [ $REGISTER_CAT -eq 1 ]; then
      (   
        for (( subrun=${SUBRUNSTART}; subrun<=${SUBRUNEND}; subrun=$[$subrun+$nIntFileCombine] ))
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
    fi

    cd ..
    
    echo "Uploading run $run ..."
    
    let iRun=$(($iRun+1))
    if [ $iRun == $nRunsToCopy ]; then
	echo "Waiting for run $run...."
	iRun=0
	wait
    fi

done # run
