#!/usr/bin/env python

"""
Cancel FTS transfers by channel
e.g. ./RemoveChannelFTS.py -c RALLCG2-CATRIUMFT2K
jonathan perkin 20110411
"""

import os
import sys
from subprocess import Popen, PIPE
import optparse
import datetime
import ND280GRID
from ND280GRID import rmNL
    
# Parser Options
parser = optparse.OptionParser()
parser.add_option("-c","--channel",
                  dest="channel",
                  type="string",
                  help="FTS channel from which to cancel jobs e.g. CATRIUMFT2K-RALLCG2")
parser.add_option("-s","--service",
                  dest="service",
                  type="string",
                  help="FTS transfer service endpoint [optional]")
(options,args) = parser.parse_args()

channel = options.channel
if not channel:
    sys.exit("Please specify an FTS channel e.g. --channel CATRIUMFT2K-RALLCG2")

service = options.service
if not service:
    print 'No FTS service endpoint specified, using Service Discovery'

## List the transfers on specified channel
command = "glite-transfer-list"
if service:
    command+=" -s "+service
command+=" -o t2k.org -c "+channel
print command

p      = Popen([command],shell=True,stdout=PIPE,stderr=PIPE)
lines  = p.stdout.readlines()
errors = p.stderr.readlines()

## Check for errors
if errors:
    print '\n'.join(errors)
    sys.exit()

## Loop over transfers and cancel
for line in lines:

    print "Cancelling transfer:"+rmNL(line)
    id = rmNL(line).split('\t')[0]

    command="glite-transfer-cancel"
    if service:
        command+=" -s "+service
    command+=" "+id

    print command

    p      = Popen([command],shell=True,stdout=PIPE,stderr=PIPE)
    lines  = p.stdout.readlines()
    errors = p.stderr.readlines()
    
    for output in [lines,errors]:
        if len(output):
            print output
