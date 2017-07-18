#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production.  Takes care of generating the config files also.
import os
import sys
import commands
import shutil
import subprocess
from sand_neutMC_config import generateConfig



from production_condition import ProductionCondition
from production_condition import SubmissionScript
from production_utilities import getRandom


condition = ProductionCondition()

run = int(sys.argv[1])
init_subrun = int(sys.argv[2])

print "Resub run = " + str(run) + " initial subrun = " + str(init_subrun)

run_dir = condition.numcdir + "/" + str(run)
os.chdir(run_dir)

script = SubmissionScript(run_dir,run,init_subrun,"23:00:00")
    
    
for subset in range(0,6):

    subrun = init_subrun + subset
    sub_dir = run_dir + "/" + str(subrun)

    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)

    os.mkdir(sub_dir)
        
    configname = generateConfig(run,subrun,condition)
        
    script.add_thread(sub_dir,configname)
        
filename = script.write_file()
        
command = "qsub " + filename
print command

os.system(command)
