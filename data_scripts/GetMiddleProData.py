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

# Parser Options

parser = optparse.OptionParser()
## Common with genie_setup
parser.add_option("-r","--run",dest="run",type="string",help="Run number of file you wish to get")
parser.add_option("-l","--level",dest="level",type="string",help="Level of processing you wish to retrieve, E.g. anal, cali, reco")
parser.add_option("-s","--subrun",dest="subrun",type="string",help="Sub-run number of file you wish to get. If left blank all sub runs in the run are downloaded")
parser.add_option("-d","--destination",dest="destination",type="string",help="Destination directory")

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

rundir=ND280GRID.RunRange(run)

lfcdir='lfn:/grid/t2k.org/nd280/v7r19p1/' + level + '/ND280/ND280/' + rundir + '/'

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
    print 'Run ' + run + ' not in ' + f.GetRunNumber()
    if run == f.GetRunNumber():
        if not subrun:
            f.Copy(dest_dir)
        elif subrun == f.GetSubRunNumber():
            f.Copy(dest_dir)
        else:
            continue
    else:
        continue

    
