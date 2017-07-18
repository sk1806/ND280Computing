#!/usr/bin/env python 

# March 2012
# The custom job (run over files with RunCustom.py) will run the calibration jobs
# required to generate calibration constants for Run 3 data:
# Run on raw data as that is distributed everywhere
# Run (unpk and) cali through ND280Control but with modified parameters for oaCalib and tfbApplyCalib 
# Run P0DRECON.exe on these output cali files
# Run CreateControlSamples.exe on the reconstructed events to select through going muons in P0D
# Run RunOAAnalysis.exe on the selected sand muons
# copy the psmu output rootfile to the relevant directory
# copy the anal output rootfile to the relevant directory

import optparse
import os
import sys
import ND280Job
import ND280GRID
from ND280GRID import ND280File
from ND280Job import ND280Process
import random
import time


# Parser Options

parser = optparse.OptionParser()

parser.add_option("-i","--input",dest="input",type="string",help="Input to process, must be an lfn")
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to use")
parser.add_option("--useTestDB",   action='store_true', default=False, help="Prepend the DB cascade with the test DB")

(options,args) = parser.parse_args()

###############################################################################

# Main Program 
nd280ver=options.version
if not nd280ver:
    sys.exit('Please enter a version of the ND280 Software to use')

## example input is 'lfn:/grid/t2k.org/nd280/raw/ND280/ND280/00005000_00005999/nd280_00005216_0000.daq.mid.gz'
input=options.input
if not input and not 'lfn:' in input:
    sys.exit('Please enter an lfn: input file')

# directory suffix added to each stage name
dirsuff='_p0dmod'

os.system('env')

#Delay processing by random time to avoid database blocking
rt=200*random.random()
print 'Sleeping ' + str(rt) + ' seconds'
time.sleep(rt)

print 'INPUT FILE: ' + input
input_file=ND280File(input)
    
## Create Job object
print 'Job object'
fmem=20*1024*1024 #max 20GB file size
vmem= 4*1024*1024 #max 4GB memory
tlim=24*3600      #max 24h running
dbtime = 2038-01-01

modules="oaCalib"
modulelist = []
if modules:
    modulelist = modules.split(',')
    print modulelist
evtype = 'spill'
config = '[calibrate],par_override=P0DMOD.PARAMETERS.DAT'
j=ND280Process(nd280ver, input_file, "Raw", evtype, modulelist, config, dbtime, fmem, vmem, tlim)

## use the test DataBase?
if options.useTestDB:
    j.useTestDB=True

## Build up the path lfn:/grid/t2k.org/nd280/calib/v*r*p*/ND280/ND280/0000*000_0000*999/[filetype]
path_prot = 'lfn:/grid/t2k.org/nd280/calib/' + nd280ver + '/ND280/ND280/' + input_file.GetRunRange() + '/'
path_end  = ''

## Copy across the root files, register some
#Remove files from list if respin
#cata, logf, cnfg always copied
dirlist=[]
copyfiles=['psmu','anal']
dirlist=copyfiles


##Test that we are able to copy a test file
print 'Testing copy'
j.TestCopy(path_prot, path_end, dirsuff, ND280GRID.GetDefaultSE())

## Run the Job
#print 'Running quick job'
#j.SetQuick()

## calibration
j.RunRaw()

## reconstruction
j.RunP0DRecon()

## sand muon selection
j.RunP0DControlSample()

## oaAanalysis
j.RunOAAnalysis()

print 'Copy files'
j.CopyRootFiles(path_prot, path_end, dirlist, dirsuff, ND280GRID.GetDefaultSE())
j.CopyLogFile(path_prot, path_end, dirsuff, ND280GRID.GetDefaultSE())

print 'Finished OK'


