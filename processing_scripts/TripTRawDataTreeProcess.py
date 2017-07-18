#!/usr/bin/env python 

# Custom job script that downloads and installs ecalUtils and then executes
# the GenTripTRawDataTree.exe app and uploads output to the GRID

import os
import sys
from ND280GRID import *
from ND280Job import *
import random
import time
import re

## Parser Options
parser = optparse.OptionParser()
parser.add_option("-i","--input",  help="Input file to process, must be an LFN")
parser.add_option("-v","--version",help="Version of nd280 software to use")
(options,args) = parser.parse_args()

if not options.input or not options.version:
    parser.print_help()
    sys.exit(1)

## Delay processing by random time to avoid database blocking
rt=200*random.random()
print 'Sleeping ' + str(rt) + ' seconds'
time.sleep(rt)

## Create ND280Job base object and change to CE working directory
j = ND280Job(options.version)
os.chdir(j.base)
print 'PWD: '+os.getcwd()

## Instantiate the input file
print 'INPUT FILE: ' + options.input
input_file = ND280File(options.input)

## Make a local copy of the input file 
local_input_name = input_file.CopyLocal(j.base,GetDefaultSE())
if not local_input_name: print 'Unable to make local copy of '+local_input_name; sys.exit(1)

## Check out ecalUtils v1r3
ecalUtilsVer    = 'v1r3'
ecalUtilsCMTDir = j.base+'/ecalUtils/'+ecalUtilsVer+'/cmt'
rtc = j.RunCommand('cmt co -r '+ecalUtilsVer+' ecalUtils')
if rtc: print 'Failed to checkout ecalUtils '+ecalUtilsVer; sys.exit(1)

os.chdir(ecalUtilsCMTDir)
print 'PWD: '+os.getcwd()
rtc = j.RunCommand('cmt make clean && cmt make')
if rtc: print 'Failed to make ecalUtils'; sys.exit(1)
os.chdir(j.base)
print 'PWD: '+os.getcwd()

## Need to source ecalUtils setup script before running any local commands
source_cmd  = 'source '+ecalUtilsCMTDir+'/setup.sh\n'
source_cmd += 'echo $PATH\n'

## Process the input file,
command = source_cmd + 'GenTripTRawDataTree.exe '+input_file.filename
rtc = j.RunCommand(command)
if rtc: print 'Unable to process '+intput_file.filename; sys.exit(1)

## List contents of  working directory, processed file should be there
print '\n'.join(os.listdir(os.getcwd()))

## Register output
print 'Registering output'
output_path = 'lfn:/grid/t2k.org/nd280/'+options.version+'/timeslip/ND280/ND280/'+input_file.GetRunRange()+'/'
output_name = 'timesliptree_'+input_file.filename.replace('daq.mid.gz','root')
output_file = ND280File(output_name)
output_ok   = output_file.Register(output_path,GetDefaultSE())
if not output_ok: print 'Unable to register output '+output_name; sys.exit(1)

print 'Finished OK'
sys.exit(0)


