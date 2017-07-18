#!/usr/bin/env python 

# Custom job script that downloads and installs ecalUtils then runs event_skim.exe and LITest.exe on input file in turn

from ND280GRID import *
from ND280Job  import *
import os
import random
import re
import stat
import sys
import time

## Parser Options
parser = optparse.OptionParser()

parser.add_option("-i","--input",  help="Input file to process, must be an LFN")
parser.add_option("-v","--version",help="Version of nd280 software to use")
(options,args) = parser.parse_args()

if not options.input or not options.version:
    parser.print_help()
    sys.exit(1)

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


# source the ecalUtils setup script in each sub process in order to find the necessary commands
source_cmd = 'source $VO_T2K_ORG_SW_DIR/ecalUtilsv1r7/setup.sh\n'
source_cmd += 'echo $PATH\n'


## Run the event skimming code
skim_filename = input_file.filename.replace('daq.mid','skim.mid')
command = source_cmd + ' event_skim.exe -o ' + skim_filename + ' ' + input_file.filename
rtc = j.RunCommand(command)
if rtc: print 'Failed to skim ' + input_file.filename; sys.exit(1)


## Process the input file,
litest_filename = input_file.filename.replace('daq.mid.gz','litest.root')
command = source_cmd + 'LITest.exe --o ' + litest_filename + ' ' + skim_filename
rtc = j.RunCommand(command)
if rtc: print 'Unable to process ' + skim_filename + ' with LITest.exe'; sys.exit(1)


## List contents of  working directory, processed file should be there
print '\n'.join(os.listdir(os.getcwd()))


## Register output (cannot use CopyRootFiles since filenames do not obey standard convention)
print 'Registering output'
output_path = 'lfn:/grid/t2k.org/nd280/contrib/perkin/'+options.version+'/ND280/ND280/'+input_file.GetRunRange()+'/'
for output in skim_filename,litest_filename:
    output_file = ND280File(output)
    output_ok   = output_file.Register(output_path,GetDefaultSE())
    if not output_ok: print 'Unable to register output '+output_name; sys.exit(1)

print 'Finished OK'
sys.exit(0)


