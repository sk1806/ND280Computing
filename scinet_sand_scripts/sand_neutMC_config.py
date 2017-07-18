#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production.  Takes care of generating the config files also.
import os
import sys
import commands

import subprocess

from production_condition import ProductionCondition
from production_condition import SubmissionScript
from production_utilities import getRandom

def generateConfig(run,subrun,conditions):
        
    """Method to generate the config file."""
        
    configname = (conditions.numcdir + "/" + str(run) + "/" + str(subrun) 
                  + "/numc_config_" + str(run) + "_" + str(subrun) + ".cfg")
    
    configContents = ""
        
    configContents += "[software]\n"
    configContents += "neut_setup_script = " + conditions.genev_setup +"\n"
    #/project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/setup.sh\n"

    configContents += "[geometry]\n"

    configContents += "baseline = " + conditions.geometry +"\n"
    if conditions.waterair == "water":
        configContents += "p0d_water_fill = 1\n"
    else:
        configContents += "p0d_water_fill = 0\n"
    
    configContents += """
    
[configuration]
module_list = neutMC

[filenaming]
"""
    configContents += "comment = " + conditions.comment + "\n"
    configContents += "run_number = " + str(run) +"\n"
    configContents += "subrun = " + str(subrun) + "\n"

    configContents += """                                                                                        

[neutrino]
neut_card = /scratch/t/tanaka/T2K/sand_production/neut_mod.card

"""

    #configContents += "flux_file_path = " + conditions.ram_disk + "/" + conditions.flux_base

    #configContents += """     
#flux_file_start = 1
#flux_file_stop = 300
#"""

    configContents += "flux_file = " + conditions.ram_disk + "/" + conditions.flux_file + "\n"


    configContents += "maxint_file = " + conditions.maxint_file_local + "\n"

    configContents += """                                           
pot = 2.5e17    
neutrino_type = beam
flux_region = SAND 
master_volume = World                                                                                           
force_volume_name = true
random_start = 1
"""

    configContents += "random_seed = " + str(getRandom()) +"\n"
    configContents += "neut_seed1 = " + str(getRandom())+"\n"   
    configContents += "neut_seed2 = " + str(getRandom())+"\n"   
    configContents += "neut_seed3 = " + str(getRandom())+"\n"   

    #print configContents

    try:
        macFile = open(configname,"w")
        macFile.write(configContents)
            
    except:
        print "can't write config file" 
            

    return configname


