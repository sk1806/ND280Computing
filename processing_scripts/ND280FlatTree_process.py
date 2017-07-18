#!/usr/bin/env python 

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

parser.add_option("-i","--input",      default='', help="Input to process, must be an lfn"         )
parser.add_option("-v","--version",    default='', help="Version of nd280 software to use"         )
parser.add_option("-p","--prod",       default='', help="Production, e.g. 4A"                      )
parser.add_option("-t","--type",       default='', help="Production type, e.g. mcp or mcpverify"   )
parser.add_option("--highlandVersion", default='', help="Version of nd280Highland2 to process with")
(options,args) = parser.parse_args()

###############################################################################

# Main Program 
if not options.version: 
    sys.exit('Please enter a version of the ND280 Software to use')
if not options.input and not 'lfn:' in options.input: 
    sys.exit('Please enter an lfn: input file')
if not options.highlandVersion:
    sys.exit('Please specify a version of nd280Highland2 to process with')

print 'INPUT FILE: ' + options.input
inputFile=ND280File(options.input)
    
## Create Job object
print 'Job object'
j=ND280Process(options.version, inputFile, 'FlatTree')

## Run the Job
print 'Running job'
j.SetHighlandVersion(options.highlandVersion)
j.RunCreateFlatTree()

## Build up the file path progenitor and end
path_prot=os.path.dirname(options.input).rstrip('anal') # naturally assume we're processing an oaAnalysis file
path_end=''                                             

# Copy across the root files, register some
dirlist=['flat'+options.highlandVersion]               # puts output into flatv*r* subfolder

print 'Copy files'
j.CopyRootFiles(path_prot, path_end, dirlist, '', ND280GRID.GetDefaultSE())

# if you got to here, the job ran to completion
print 'Finished OK'
