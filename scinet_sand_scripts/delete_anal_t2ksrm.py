#!/usr/bin/env python 
#Copy files to t2ksrm
import os
import sys
import commands
import glob

import subprocess

from production_condition import ProductionCondition
from production_condition import SubmissionScript
from production_utilities import getRandom

from sand_neutMC_config import generateConfig


def get_file(run,subrun,conditions,dataTier):

    basedir = conditions.g4analdir
    if dataTier == "numc":
        basedir = conditions.numcdir
    inputfilename = (basedir + "/" + str(run) + "/" + str(subrun)
                  + "/oa_nt_beam_" + str(run) + "-*" + str(subrun) + "*_" + dataTier + "_000*.root"
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
        sys.exit()

    filename = inputfile[0].split("/")[len(inputfile[0].split("/"))-1]
    return inputfile[0],filename
        


# ____________________________________________________________________________
# Start by checking that we are running on datamover1

host = os.getenv("HOSTNAME")

if host != "gpc-logindm01":
    print "You must execute this script on data mover1. Exiting"
    sys.exit()




condition = ProductionCondition()

dataTier = "sand"

#for run in range(condition.run+97,condition.run+98):
for run in range(condition.run+0,condition.run+1):

    # create the output directory for this run
    run_dir = condition.numcdir + "/" + str(run)

    os.chdir(run_dir)

    for subrun in range(0,120):

        fullfilename,filename = get_file(run,subrun,condition,dataTier)
        
        #print filename

        command = "lcg-del -a lfn:/grid/t2k.org/nd280/"+ str(condition.grid_dir) + "/" + dataTier + "/" + filename
        print command
        #os.system(command)

        
