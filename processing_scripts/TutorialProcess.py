#!/usr/bin/env python 

# Custom job script that runs nd280Highland2/v1r7 RunCreateFlatTree.exe and RunNumuCCMultiPiAnalysis.exe 

from ND280GRID import *  # lazy includes
from ND280Job  import *
import os
import sys

## Parser Options
parser = optparse.OptionParser()

## ND280Job requires these inputs
parser.add_option("-i","--input",  help="Input file to process, must be an LFN", default=''                        )
parser.add_option("-v","--version",help="Version of nd280 software to use",      default='v11r31'                  )

## This is an additional option for develpment testing
parser.add_option("-l", "--local", help="Run locally?", default=False, action='store_true')
(options,args) = parser.parse_args()

if not options.input or not options.version:
    parser.print_help()
    sys.exit(1)

## Create ND280Job base object and change to CE working directory
j = ND280Job(options.version)

## Run in /scratch?
if options.local: 
    print 'Running locally'
    j.base = '/scratch/%s'  % os.getenv('USER')
    print 'In directory %s' % j.base
    
os.chdir(j.base)
print 'PWD: '+os.getcwd()

## Instantiate the input file object
print 'INPUT FILE: ' + options.input
input_file = ND280File(options.input)

## Make a local copy of the input file? (May already exist if developing job script locally 
## and don't want to download again unnecessarily...)
anal_filename = os.path.basename(options.input)
if not os.path.exists(anal_filename):
    local_input_name = input_file.CopyLocal(j.base,GetDefaultSE()) # finds nearest replica
    if not local_input_name: print 'Unable to make local copy of '+local_input_name; sys.exit(1)

## Need to source nd280Highland2/v1r7 setup script before running any local commands
source_cmd  = 'source %s/nd280Highland2v1r7/setup.sh; ' % os.getenv('VO_T2K_ORG_SW_DIR')

## Create an output file name
flat_filename = anal_filename.replace('_anal_','_flatv1r7_')

## Process the anal file,
exe = 'RunCreateFlatTree.exe'
command = source_cmd + exe + ' -p highlandIO.parameters.dat -o ' + flat_filename + ' ' + anal_filename
rtc = j.RunCommand(command)
if rtc: print 'Unable to process ' + anal_filename + ' with ' + exe; sys.exit(1)

## Now process the flat file with multi-pi anlysis
exe = 'RunNumuCCMultiPiAnalysis.exe'
multi_filename = anal_filename.replace('_anal_','_multipiv1r7_')
command = source_cmd + exe + ' -o ' + multi_filename + ' ' + flat_filename
rtc = j.RunCommand(command)
if rtc: print 'Unable to process ' + flat_filename + ' with ' + exe ; sys.exit(1)

## List contents of  working directory, processed file should be there
print '\n'.join(os.listdir(os.getcwd()))

## Don't register output if running locally
if options.local:
    sys.exit(0)

## Register output in your contrib area...
print 'Registering output'
output_path = 'lfn:/grid/t2k.org/nd280/contrib/perkin/'
for output in flat_filename,multi_filename:
    output_file = ND280File(output)
    output_ok   = output_file.Register(output_path,GetDefaultSE())
    if not output_ok: print 'Unable to register output '+output_name; sys.exit(1)

print 'Finished OK'
sys.exit(0)













