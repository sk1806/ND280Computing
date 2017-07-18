#!/usr/bin/env python

"""
A script to get middle pass processed files from the LFC

Any other suggestions please e-mail me, b.still@qmul.ac.uk
"""

import ND280GRID
from ND280GRID import ND280Dir
from ND280GRID import ND280File
import optparse
import os
import sys

# Parser Options

parser = optparse.OptionParser()
## Common with genie_setup
parser.add_option("-r","--run",dest="run",type="string",help="Run number of file you wish to get")
parser.add_option("-l","--level",dest="level",type="string",help="Level of processing you wish to retrieve, E.g. anal, cali, reco")
parser.add_option("-s","--subrun",dest="subrun",type="string",help="Sub-run number of file you wish to get. If left blank all sub runs in the run are downloaded")
parser.add_option("-d","--destination",dest="destination",type="string",help="Destination directory")

### MC specific options
parser.add_option("-n","--neutrino",dest="neutrino",type="string",help="Neutrino Generator")
parser.add_option("-g","--geo_baseline",dest="geo_baseline",type="string",help="Geometry Baseline")
parser.add_option("-a","--area",dest="area",type="string",help="Area of ND280, E.g. basket or magnet")
parser.add_option("-t","--trigger",dest="trigger",type="string",help="Trigger used: beam. Also contains cherry picked for baseket area files: nue, ncpizero, ccpizero")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

run=options.run
if not run:
    sys.exit('Please give a run number using the -r flag')
run=ND280GRID.PadOutRun(run)

destination=options.destination
if not destination:
    sys.exit('Please state a destination where you would like the files copied to using the -d flag.')

level=options.level
if not level:
    sys.exit('No level specified with -l flag')

subrun=options.subrun
if not subrun:
    print 'No subrun specified with the -s flag so I will get all subruns for run ' + run

neutrino=options.neutrino
if not neutrino:
    neutrino='genie'
    print 'Setting the neutrino generator option to default: ' + neutrino 

geo_baseline=options.geo_baseline
if not geo_baseline:
    geo_baseline='2010-02-water'
    print 'Setting the geo_baseline option to default: ' + geo_baseline

area=options.area
if not area:
    area='magnet'
    print 'Setting the area option to default: ' + area

trigger=options.trigger
if not trigger:
    trigger='beam'
    print 'Setting the trigger option to default: ' + trigger

rundir=ND280GRID.RunRange(run)

lfcdir='lfn:/grid/t2k.org/nd280/mcp1/' + neutrino + '/' + geo_baseline + '/' + area + '/' + trigger + '/' + level + '/'

try:
    source_dir=ND280Dir(lfcdir)
except:
    sys.exit('Could not see ' + lfcdir + ' please double check it exists.')

try:
    dest_dir=ND280Dir(destination)
except:
    sys.exit('Could not see ' + destination + ' please double check it exists.')


for file_name,size in source_dir.dir_dic.iteritems():
    if not run in file_name:
        continue
    f=ND280File(source_dir.dir + '/' + file_name)
    if run == f.GetRunNumber():
        if not subrun:
            f.Copy(dest_dir)
        elif subrun == f.GetSubRunNumber():
            f.Copy(dest_dir)
        else:
            continue
    else:
        continue

    
