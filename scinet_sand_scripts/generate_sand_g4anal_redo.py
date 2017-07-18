#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production for the g4mc to anal stage.  Takes care of generating the config files also.
# Produced with
# grep 'FATAL ERROR' /scratch/t/tanaka/T2K/sand_production/production005/F/mcp/neut/2010-11-water/sand/beamc/g4anal/903170*/*/*log  
#
import os
import sys
import glob
import subprocess
import shutil

from production_condition import ProductionCondition
from production_condition import SubmissionScript
from production_utilities import getRandom

def generateConfig(run,subrun,conditions):
        
    """Method to generate the config file."""
        
    configname = (conditions.g4analdir + "/" + str(run) + "/" + str(subrun) 
                  + "/g4anal_config_" + str(run) + "_" + str(subrun) + ".cfg")
    
    configContents = ""
        
    configContents += """
[geometry]
"""
    configContents += "baseline = " + conditions.geometry +"\n"
    if conditions.waterair == "water":
        configContents += "p0d_water_fill = 1\n"
    else:
        configContents += "p0d_water_fill = 0\n"
    
    configContents += """    
[configuration]
module_list = sandPropagate nd280MC elecSim oaCalibMC oaRecon oaAnalysis
"""
    inputfilename = (conditions.numcdir + "/" + str(run) + "/" + str(subrun)
                  + "/oa_nt_beam_" + str(run) + "-*" + str(subrun) + "*_numc_000*.root"
                 )
    inputfile = glob.glob(inputfilename)
    #print inputfile 

    if len(inputfile) != 1:
        print ("We have wrong number of potential input files. N=" + str(len(inputfile))
               + "; should be 1.")
        print "Files are:"
        print inputfile
        print "input = " + inputfilename
        print "Run is " + str(run) + "/" + str(subrun)
        #sys.exit()
    else:
        local_filename = conditions.ram_disk + "/" + inputfile[0].split("/")[len(inputfile[0].split("/"))-1]
        #print "FFFF" + local_filename
        
        configContents += "inputfile = "+ local_filename +" \n\n"
        #configContents += "inputfile = "+ inputfile[0] +" \n\n"                                                                                 



    configContents += "[filenaming]\n"
    configContents += "comment = " + conditions.comment + "\n"
    configContents += "run_number = " + str(run) +"\n"
    configContents += "subrun = " + str(subrun) + "\n"

    configContents += """                                                                                       
[sandPropagate]
num_events = 10000000

[nd280mc]
num_events = 10000000
mc_type = Neut_RooTracker
nbunches = 8
interactions_per_spill = 100.4
pot_per_spill = 9.463e+13
bunch_duration = 19
mc_full_spill = 1
time_offset = 50
count_type = MEAN
mc_position = free  
"""

    configContents += "random_seed = " + str(getRandom()) +"\n"

#    print configContents

    try:
        macFile = open(configname,"w")
        macFile.write(configContents)
            
    except:
        print "can't write config file" 
            

    return configname,inputfile[0],local_filename





condition = ProductionCondition()



#list_fails = [["90307004","65"],["90307005","33"],["90307008","73"],["90307009","87"],["90307010","63"],["90307012","48"],["90307012","49"],["90307012","50"]]
#list_fails = [["90307012","51"],["90307012","52"],["90307012","53"],["90307012","54"],["90307012","55"],["90307013","37"],["90307014","114"],["90307021","60"]]
#list_fails = [["90307022","6"],["90307032","87"],["90307035","21"],["90307037","46"]]
list_fails = [["90317001","104"],["90317002","16"],["90317003","14"],["90317005","1"],["90317008","51"],["90317008","97"],["90317011","50"],["90317018","96"]]
#list_fails = [["90317022","111"],["90317022","92"],["90317025","69"],["90317028","76"],["90317030","104"],["90317034","12"]]


print list_fails

# Just name the output file using the first fail

run = list_fails[0][0]
subrun = list_fails[0][1]
print run + " " + subrun


run_dir = condition.g4analdir + "/" + str(run)
os.chdir(run_dir)


script = SubmissionScript(run_dir,run,subrun,"10:00:00",condition,False)

for runsub in list_fails:
#    print runsub
    run  = runsub[0]
    subrun = runsub[1]

    print run + " " + subrun
    run_dir = condition.g4analdir + "/" + str(run)
    sub_dir = run_dir + "/" + str(subrun)

    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
        
    os.mkdir(sub_dir)


    #configname = generateConfig(run,subrun,condition)
    #ram_dir = condition.ram_disk + "" + str(run) + "/" + str(subrun)
    #script.add_numc_thread(sub_dir,configname,ram_dir )
    configname,global_inputfile,local_inputfile = generateConfig(run,subrun,condition)

    script.add_thread(sub_dir,configname,global_inputfile,local_inputfile)
            

filename = script.write_file()

command = "qsub " + filename
print command
os.system(command)


