#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production.  Takes care of generating the config files also.
import os
import sys
import shutil
import commands

import subprocess

from production_condition import ProductionCondition
from production_condition import SubmissionScript
from production_utilities import getRandom

from neutMC_config import generateConfig
#from neutMC_config_tpcgas import generateConfig


condition = ProductionCondition()

#for run in range(condition.run+10,Condition).run+40):
# 12 jobs, each with 7*8 neut productions, ie. 56 files, is 3.36e20 POT
njobs=56   #16  #40          #56  #200

#for DEBUG:
start_job=0

#for run in range(condition.run+0,condition.run+75):    #for 2.1e21 POT
for run in range(condition.run+0,condition.run+125):    #for 3.5e21 POT
#for run in range(condition.run+0,condition.run+110):    #for 3.1e21 POT
#for run in range(condition.run+0,condition.run+33):    #for 9.24e20 POT
#for run in range(condition.run+0,condition.run+43):    #for 1.2e21 POT
#for run in range(condition.run+0,condition.run+40):    #for 1.1e21 POT
#for run in range(condition.run+0,condition.run+20):    #for 1.1e21 POT with 1e18 for basket

#for run in range(condition.run+0,condition.run+10):    #for 1.6e22 POT w 2e19 for basket cherrypicked
#for run in range(condition.run+0,condition.run+24):    


    # create the output directory for this run
    run_dir = condition.numcdir + "/" + str(run)
    if not os.path.exists(run_dir):
        os.makedirs(run_dir)

    os.chdir(run_dir)

    for setn in range(0,1):

        script = SubmissionScript(run_dir,run,setn*njobs,"24:00:00",condition,True)
        
        for subset in range(0,njobs):
            
            if subset < start_job:
                continue
            subrun = setn*njobs+subset
            sub_dir = run_dir + "/" + str(subrun)

            if os.path.exists(sub_dir):
                shutil.rmtree(sub_dir)

            os.mkdir(sub_dir)
            
            ##if not os.path.exists(sub_dir):
            ##    os.mkdir(sub_dir)

            configname = generateConfig(run,subrun,condition)

            #ram_dir = condition.ram_disk + "" + str(run) + "/" + str(subrun)
            # All in one dir to share the symlinks) OR only use ram_disk and keep subdirs 
            #(won't be counted to diskQuota) ??
            ram_dir = condition.ram_disk
            script.add_numc_thread(sub_dir,os.path.basename(configname),ram_dir,subrun)
            
            if (subrun%8 == 7 or subrun == njobs-1):
                script.add_wait_and_check_exitcode()

                #clean out this and all previous 7 subruns when the processes are done
                # NOT necessary anymore because I work on the RAMdisk, which is cleaned at the end of the job!
                for i in range(subrun-7, subrun+1):
                #    script.clean_directory(run_dir,i)
                    script.copy_output(ram_dir,run_dir,run,i)

        filename = script.write_file()

        command = "qsub " + filename
        print command
        
        os.system(command)
        
