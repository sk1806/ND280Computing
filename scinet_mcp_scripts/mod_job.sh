#!/bin/bash
#
#############################################################################
#
# Title: SciNet Job Modification Script
#
# Usage: This script contains methods for modifying job attributes or deleting
#        jobs that have been submitted to the cluster. There are currently no
#        command-line arguments and modifications must be hardcoded.
#
#############################################################################

# Get the list of Job Ids
# The 'grep' command cuts out the header output of 'qstat' as well as filtering
# the jobs depending on what you 'grep'. Currently there is no filter (every 
# line output of 'qstat' contains <your username>).
jobIDs=(`qstat | grep "pdeperio" | cut -d'.' -f1`)

# Specify the Job Id range you wish to modify
# (currently no range)
JOBIDSTART=0
JOBIDEND=9999999

# Loop over all jobs found
for jobID in "${jobIDs[@]}"
do

    if [ $jobID ]; then

        # Apply Job Id number range
	if [ $jobID -lt $JOBIDSTART ]; then
	    continue
	fi
	if [ $jobID -gt $JOBIDEND ]; then
	    continue
	fi

        # Get info about the job. This parses the output of 'qstat' into
        # an array where:
        # JOB_INFO[0]: Job id
        # JOB_INFO[1]: Name (cutoff by qstat output, use 'checkjob' for full name)
        # JOB_INFO[2]: User
        # JOB_INFO[3]: Time Use
        # JOB_INFO[4]: State
        # JOB_INFO[5]: Queue
	JOB_INFO=`qstat | grep ${jobID}`
	JOB_INFO=(`echo "${JOB_INFO}" | awk '{
   	    n = split ( $0, a, " " )
   	    for ( i = 1; i <= n; i++ ) {     
      		printf( "%s\n", a[ i ] );
   	    }
	}'`)

	
	# Ignore jobs with specified state (R: running, Q: queued, H: hold)
        # Of course you can select jobs by replacing "!=" with "=="
	if [ "${JOB_INFO[4]}" != "Q" ]; then
	    continue;
	fi

        # Useful output to make sure you're selecting the actual jobs you want
        # (Remember to comment out the commands below if testing)
	echo "Modifying job name:" ${JOB_INFO[1]}     "State:" ${JOB_INFO[4]}
    	
	# Walltime adjustment: Decreases (cannot increase) the requeseted walltime for 
        # the job in seconds. This was only useful when I had limitted access to
        # number of nodes in parallel.
	#mjobctl -m reqawduration-=14400 $jobID

	# Delete job
	#qdel $jobID

	# Remove job dependency (if you set the dependency previously and the
        # scheduler failed to recognize the completed/failed job)
	#mjobctl -m depend= $jobID

        # Add hold to queued job
        qhold $jobID

        # Remove hold from queued job
        # qrls $jobID

	echo "-------------------------------------------"
	echo ""

    fi

done

