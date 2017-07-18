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

from sand_neutMC_config import generateConfig


condition = ProductionCondition()

#for run in range(condition.run+10,condition.run+40):
for run in range(condition.run+0,condition.run+5):

    # create the output directory for this run
    run_dir = condition.numcdir + "/" + str(run)
    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    os.chdir(run_dir)

    for setn in range(0,15):

        script = SubmissionScript(run_dir,run,setn*8,"23:00:00",condition,True)
        
        for subset in range(0,8):

            subrun = setn*8+subset
            sub_dir = run_dir + "/" + str(subrun)

            if os.path.exists(sub_dir):
                shutil.rmtree(sub_dir)

            os.mkdir(sub_dir)
            #if not os.path.exists(sub_dir):
            #    os.mkdir(sub_dir)

            configname = generateConfig(run,subrun,condition)

            ram_dir = condition.ram_disk + "" + str(run) + "/" + str(subrun)
            script.add_numc_thread(sub_dir,configname,ram_dir )
            
        filename = script.write_file(True)

        command = "qsub " + filename
        print command

        os.system(command)
