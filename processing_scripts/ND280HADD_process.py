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

parser.add_option("-i","--input",      default='', help="Input: list of files to hadd"     )
parser.add_option("-v","--version",    default='', help="Version of nd280 software to use" )
parser.add_option("-p","--prod",       default='', help="Production, e.g. 4A"                      )
parser.add_option("-t","--type",       default='', help="Production type, e.g. mcp or mcpverify"   )

(options,args) = parser.parse_args()

## The Input
print 'INPUT FILE: ' + options.input
inputFile=ND280File(options.input)
    
## Create Job object
print 'Job object'
j=ND280Process(options.version, inputFile, 'HADD')

## Run the Job, output registered internally
print 'Running job'
j.RunHADD()

# if you got to here, the job ran to completion
print 'Finished OK'
