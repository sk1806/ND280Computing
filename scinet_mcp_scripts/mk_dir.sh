#!/bin/bash
#
#############################################################################
#
# Title: SciNet ND280 MCP directory structure initialization script
#
# Usage: This script should be called from the specific sample directory,
#        e.g. in /scratch/<your username>/production004, then
#        ./mk_dir.sh 
#
#        Ensure you have the desired generators, baselines, volumes and 
#        MC types set in the arrays in sub_header.sh. The script will then create 
#        the whole directory structure as defined here:
#        http://www.t2k.org/nd280/datacomp/howtoaccessdata/directorystructure 
#        and here:
#        http://www.t2k.org/nd280/datacomp/mcproductionruns/production004.
#        Note, the actual sample configurations are generated using 
#        conditionals within the loop below.
#
#        Finally, this script will link the job submission scripts 
#        (sub_nd280.sh and sub_numc.sh) and GRID scripts into each sample 
#        directory, from where you should call them.
#
#############################################################################

# Production directory environment variable must be set by you externally
if [ "${PRODUCTION_DIR}" == "" ]; then
    echo "Please set the PRODUCTION_DIR environment variable to the root directory of your production"
    exit 1
fi

. ${PRODUCTION_DIR}/sub_header.sh

echo ""

# Note also other combinations should not created as per MC specification 
# in above link. This is controlled with conditionals in the loop below.
for RESPIN in ${RESPINS[@]}
  do

  for SIMNAME in ${SIMNAMES[@]}
    do
    
    for BASELINE in ${BASELINES[@]}
      do
      
      for VOLUME in ${VOLUMES[@]}
	do

	for MC_TYPE in ${MC_TYPES[@]}
	  do
	  
	  for STEP in ${STEPS[@]}
	    do
	    
	    # Control for magnet, spill simulated, samples
	    if [ $VOLUME == magnet ]; then 
		
		# No cherry-picked or nue samples in magnet
		if [[ $MC_TYPE != beam* ]]; then
		    continue
		fi


		# Beam spec must specified for magnet ND280 MC
		if [ $MC_TYPE == beam ]; then
		    continue
		fi
		
		# 2010-02 baseline
		if [[ $BASELINE == 2010-02* ]]; then

		    # No beam spec >a
		    if [ $MC_TYPE != beama ]; then
			continue
		    fi

		# 2010-11 baseline
		elif [[ $BASELINE == 2010-11* ]]; then
                    
                    # No beam spec 'a'
		    if [ $MC_TYPE == beama ]; then
			continue
		    fi
		    
		else
		    echo "Unspecified baseline = ${BASELINE}"
		    exit 1
		    
		fi

	    # Control for basket samples
            elif [ $VOLUME == basket ]; then

                # No basket sample for 2010-02 baseline since DSEcal is not 
                # contained in the basket volume and makes no difference if 
                # it's removed
		if [[ $BASELINE == 2010-02* ]]; then
		    continue
		fi

		# No full spill simulations
		if [[ $MC_TYPE == beam* ]]; then
		    if [ $MC_TYPE != beam ]; then
			continue
		    fi
		fi
		
	    else
		echo "Unspecified volumne of generation = ${VOLUME}"
		exit 3

            fi
	    
	    # Add "verify/nd280vers" to the GRID sample directory for verification files
	    # 'numc' vector files do not follow ND280 version number or verification
	    if [[ $VERIFY -eq 1 ]]; then
		dir=${PRODUCTION_DIR}/${RESPIN}/mcp/verify/${ND280VERS}/${SIMNAME}/${BASELINE}/${VOLUME}/${MC_TYPE}/${STEP}
	    else
		dir=${PRODUCTION_DIR}/${RESPIN}/mcp/${SIMNAME}/${BASELINE}/${VOLUME}/${MC_TYPE}/${STEP}
	    fi

	    mkdir -p ${dir}
	    
	    # Some checks that this sample is defined
	    HERE=${dir}
	    echo "Creating directory and script links for..."
	    get_mc_details
	    echo ""
	    
            if [ $STEP == numc ]; then
		mkdir -p ${dir}/setup
                ln -sf ${PRODUCTION_DIR}/sub_numc.sh ${dir}/.
            else
                ln -sf ${PRODUCTION_DIR}/sub_nd280.sh ${dir}/.
	    fi

            ln -sf ${PRODUCTION_DIR}/grid_cp.sh ${PRODUCTION_DIR}/rsync.sh ${PRODUCTION_DIR}/chkLogs.sh ${PRODUCTION_DIR}/grid_ls.sh ${PRODUCTION_DIR}/cat_cp.sh ${PRODUCTION_DIR}/mk_progress_page.sh ${dir}/.

	  done
	done
      done
    done
  done
done


