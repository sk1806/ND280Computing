#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production for the g4mc to anal stage.  Takes care of generating the config files also.
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
module_list = oaAnalysis
"""
    inputfilename = (conditions.g4analdir + "/" + str(run) + "/" + str(subrun)
                  + "/oa_nt_beam_" + str(run) + "-*" + str(subrun) + "*_reco_000*.root"
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


    oldanalfilename = (conditions.g4analdir + "/" + str(run) + "/" + str(subrun)
                  + "/oa_nt_beam_" + str(run) + "-*" + str(subrun) + "*_anal*.root"
                 )
    analfile = glob.glob(oldanalfilename)
    #print inputfile                                                                                                                              

    if len(analfile) == 1:
        os.remove(analfile[0])
    else:
        print "No anal file to remove; weird."

    oldcatfilename = (conditions.g4analdir + "/" + str(run) + "/" + str(subrun)
                      + "/oa_nt_beam_" + str(run) + "-*" + str(subrun) + "*_anal*_catalogue.dat"
                      )
    catfile = glob.glob(oldcatfilename)
    #print inputfile                                                                                                                              

    if len(catfile) == 1:
        os.remove(catfile[0])
    else:
        print "No cat file to remove; weird."



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

for run in range(condition.run+0,condition.run+1):
#for run in range(condition.run+13,condition.run+20):

    # create the output directory for this run
    run_dir = condition.g4analdir + "/" + str(run)

    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    os.chdir(run_dir)

    #for setn in range(0,15):
    for setn in range(0,1):

        script = SubmissionScript(run_dir,run,setn*8,"2:00:00",condition,False)
        
        for subset in range(0,8):

            subrun = setn*8+subset
            sub_dir = run_dir + "/" + str(subrun)

            #if os.path.exists(sub_dir):
            #    shutil.rmtree(sub_dir)

            #os.mkdir(sub_dir)

            configname,global_inputfile,local_inputfile = generateConfig(run,subrun,condition)

            #print configname + " CC " + global_inputfile + " " + local_inputfile + "!!!"
            script.add_thread(sub_dir,configname,global_inputfile,local_inputfile)
            
        filename = script.write_file()


        command = "qsub " + filename
        print command

        os.system(command)
