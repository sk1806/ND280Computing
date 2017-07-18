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
    if conditions.oldneut:
        configContents += "neut_setup_script = /project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/setup.sh\n"
    elif conditions.newoldneut:
        configContents += "neut_setup_script = /project/t/tanaka/T2K/neut/branches/5.1.4.3_nd280/src/neutgeom/setup.sh\n"
    else:
        #configContents += "neut_setup_script = /project/t/tanaka/T2K/neut/branches/5.3.1_nd280/src/neutgeom/setup.sh\n"
        #configContents += "neut_setup_script = /project/t/tanaka/T2K/neut/branches/5.3.1_nd280_wBBBA05/src/neutgeom/setup.sh\n"
        configContents += "neut_setup_script = /project/t/tanaka/T2K/neut/branches/5.3.2_nd280/src/neutgeom/setup.sh\n"
    
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

    if conditions.oldneut:
        configContents += """                                                                                        

[neutrino]
neut_card = /project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/neut.card
"""
    elif conditions.newoldneut:
        configContents += """                                                                                        

[neutrino]
neut_card = /project/t/tanaka/T2K/neut/branches/5.1.4.3_nd280/src/neutgeom/neut.card
"""
    else:
        configContents += """                                                                                        

[neutrino]
neut_card = /project/t/tanaka/T2K/neut/branches/5.3.2_nd280/src/neutgeom/neut.card
"""

    configContents += "flux_file = "  + conditions.ram_disk + "/" + conditions.flux_base + "\n"

#flux_file = flux_file
#"""

#   configContents += "flux_file_path = " + conditions.ram_disk + "/" + conditions.flux_base

#    configContents += """     
#flux_file_start = 1
#flux_file_stop = 300
#"""

    configContents += "maxint_file = " + conditions.maxint_file_local + "\n"

# default: 5e17 but for basket MC special production higher
    configContents += """                                           
pot = 5.0e17
neutrino_type = beam
"""
    if conditions.baskmagn == "basket":
        configContents += """                                           
flux_region = basket
master_volume = Basket                                                                                           
random_start = 1
"""
    elif conditions.baskmagn == "magnet":
        configContents += """                                           
flux_region = magnet
master_volume = Magnet                                                                                           
random_start = 1
"""
    else:
        print "Unknown basket/magnet condition"
        

    configContents += "random_seed = " + str(getRandom()) +"\n"
    configContents += "neut_seed1 = " + str(getRandom())+"\n"   
    configContents += "neut_seed2 = " + str(getRandom())+"\n"   
    configContents += "neut_seed3 = " + str(getRandom())+"\n"   

    configContents += "\n"
    configContents += "[nd280mc]\n"
    configContents += "mc_type=Neut_RooTracker \n"

    #print configContents

    try:
        macFile = open(configname,"w")
        macFile.write(configContents)
            
    except:
        print "can't write config file" 
            

    return configname


