#!/usr/bin/env python 
# A script for generating the submission script for scinet sand muon
# production.  Takes care of generating the config files also.

# To make list of failures:
# ll -S /scratch/t/tanaka/T2K/sand_production/production005/F/mcp/neut/2010-11-air/sand/beamc/numc/903070*/*/*log | gawk '{if($5 == 0) printf"%s \n",$9}' > fail.raw
# or
# ll -S /scratch/t/tanaka/T2K/sand_production/production005/F/mcp/neut/2010-11-water/sand/beamc/numc/903170*/*/*log | gawk '{if($5 == 0) printf"%s \n",$9}' > fail_water2.raw
# or
# 
# and make list:
# get_fail.py
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


#list_fails = [["90307000","22"],["90307000","27"]]
#list_fails = [["90307001","79"],["90307002","18"],["90307003","95"],["90307004","88"],["90307005","47"],["90307007","8"],["90307009","6"],["90307009","86"]]
#list_fails = [["90307014","31"],["90307015","99"],["90307016","68"],["90307018","23"],["90307018","41"],["90307019","87"],["90307020","39"],["90307021","77"]]
#list_fails = [["90307022","101"],["90307023","110"],["90307023","54"],["90307025","28"],["90307025","40"],["90307026","96"],["90307030","22"],["90307030","71"]]
#list_fails = [["90307031","39"],["90307031","6"],["90307032","81"],["90307032","85"],["90307039","66"]]
#list_fails = [["90307001","18"],["90307003","95"],["90307004","88"],["90307005","47"],["90307007","8"],["90307009","6"],["90307009","86"]]
#list_fails = [["90307014","99"],["90307016","68"],["90307018","23"],["90307018","41"],["90307019","87"],["90307020","39"],["90307021","77"]]
#list_fails = [["90307022","110"],["90307023","54"],["90307025","28"],["90307025","40"],["90307026","96"],["90307030","22"],["90307030","71"]]
#list_fails = [["90307031","81"],["90307032","85"],["90307039","66"]]
#list_fails = [["90307001","47"],["90307022","28"]]
#list_fails = [["90307015","73"],["90307034","89"],["90307015","7"],["90307033","115"],["90307029","86"],["90307003","33"],["90307026","29"],["90307029","56"]]
#list_fails = [["90307025","23"],["90307021","62"],["90307019","30"],["90307029","104"],["90307038","39"],["90307027","91"]]
#list_fails = [["90317004","89"],["90317005","58"],["90317010","79"],["90317014","78"],["90317015","92"],["90317019","85"],["90317020","118"],["90317021","39"]]
#list_fails = [["90317021","80"],["90317022","118"],["90317022","43"],["90317023","22"],["90317025","56"],["90317029","106"]]
#list_fails = [["90317005","58"],["90317031","106"],["90317033","97"],["90317035","36"],["90317038","25"],["90317038","56"],["90317038","57"],["90317038","58"]]
#list_fails = [["90317038","59"],["90317038","60"],["90317038","61"],["90317038","62"],["90317038","63"]]
#list_fails = [["92307002","48"],["92307002","66"]]

# 6B old-NEUT run-3, air
# list_fails = [["92307000","54"],["92307000","82"],["92307001","26"],["92307002","71"],["92307003","7"],["92307005","112"],["92307007","67"],["92307009","102"]]
#list_fails = [["92307009","34"],["92307009","48"],["92307009","49"],["92307009","50"],["92307009","51"],["92307009","52"],["92307009","53"],["92307009","54"]]
#list_fails = [["92307009","55"],["92307012","35"],["92307013","21"],["92307013","62"],["92307013","82"],["92307013","96"],["92307015","111"],["92307016","13"]]
#list_fails = [["92307016","98"],["92307019","67"],["92307020","68"],["92307021","83"],["92307022","32"],["92307023","84"],["92307024","17"],["92307024","32"]]
#list_fails = [["92307025","100"],["92307025","101"],["92307025","102"],["92307025","103"],["92307025","71"],["92307025","96"],["92307025","97"],["92307025","98"]]
#list_fails = [["92307025","99"],["92307028","6"],["92307029","28"],["92307032","38"],["92307032","64"],["92307033","103"],["92307033","26"],["92307034","82"]]
#list_fails = [["92307036","89"],["92307037","106"],["92307037","17"],["92307037","49"],["92307038","69"],["92307038","85"],["92307039","30"],["92307039","97"]]

# New NEUT Air
#list_fails = [["90307000","27"],["90307004","4"],["90307007","83"],["90307010","88"],["90307011","91"],["90307015","109"],["90307015","76"],["90307018","74"]]
#list_fails = [["90307019","34"],["90307021","21"],["90307021","27"],["90307021","99"],["90307023","20"],["90307023","45"],["90307025","16"],["90307026","75"]]
#list_fails = [["90307028","42"],["90307031","84"],["90307032","64"],["90307033","25"],["90307033","48"],["90307036","114"],["90307037","66"],["90307038","93"]]
list_fails = [["90307039","6"],["90307039","74"],]



print list_fails
# Just name the output file using the first fail

run = list_fails[0][0]
subrun = list_fails[0][1]
print run + " " + subrun


run_dir = condition.numcdir + "/" + str(run)
os.chdir(run_dir)


script = SubmissionScript(run_dir,run,subrun,"18:00:00",condition,True)

for runsub in list_fails:
#    print runsub
    run  = runsub[0]
    subrun = runsub[1]

#    print run + " " + subrun
    run_dir = condition.numcdir + "/" + str(run)
    sub_dir = run_dir + "/" + str(subrun)

    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
        
    os.mkdir(sub_dir)


    configname = generateConfig(run,subrun,condition)

    ram_dir = condition.ram_disk + "" + str(run) + "/" + str(subrun)
    script.add_numc_thread(sub_dir,configname,ram_dir )


filename = script.write_file(True)

command = "qsub " + filename
print command

os.system(command)


sys.exit()

#for run in range(condition.run+10,condition.run+40):
for run in range(condition.run,condition.run+1):

    # create the output directory for this run
    run_dir = condition.numcdir + "/" + str(run)
    if not os.path.exists(run_dir):
        os.mkdir(run_dir)

    os.chdir(run_dir)

    for setn in range(0,15):

        script = SubmissionScript(run_dir,run,setn*8,"9:00:00",condition,True)
        
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
            
        filename = script.write_file(true)

        command = "qsub " + filename
        print command

#        os.system(command)
