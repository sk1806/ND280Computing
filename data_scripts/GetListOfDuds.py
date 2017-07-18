#!/usr/bin/env python

"""
Generate a list of dud ('source file doen't exist') transfers

jonathan perkin 20110309
"""

import ND280GRID
from ND280GRID import runLCG
import os
import sys
import optparse


# Parser Options
parser = optparse.OptionParser()
parser.add_option("-c","--channel",  dest="channel",  type="string",help="FTS Channel to search for dud transfers")
parser.add_option("-t","--transfers",dest="transfers",type="string",help="FTS transfers file to search for duds")
(options,args) = parser.parse_args()


# FTS Channel
channel = options.channel
command = "glite-transfer-channel-list"
lines,errors = runLCG(command)
if errors:
    sys.exit("Unable to "+command)

allowed_channels = []
for line in lines:
    allowed_channels.append(ND280GRID.rmNL(line))
    
if not channel in allowed_channels:
    sys.exit("Please specify FTS channel")


# Environment
service = os.getenv("FTS_SERVICE")
if not service:
    service = "https://lcgfts.gridpp.rl.ac.uk:8443/glite-data-transfer-fts/services/FileTransfer"
    os.environ["FTS_SERVICES"]=service
    


# Duds log file
log_name = "duds.log"
log_file = open(log_name,'w')


# Get list of failed transfer IDs
IDs = []
transfers = options.transfers

if transfers:
    # Get IDs from transfers file
    transfers_file = open(transfers,'r')
    lines = transfers_file.readlines()
    transfers_file.close()
    
    for line in lines:
        IDs.append(ND280GRID.rmNL(line))

else:
    # Get IDs from FTS
    state = "Failed"
    command = "glite-transfer-list -s "+service+" -c "+channel+" "+state
    lines,errors=runLCG(command)
    if errors:
        sys.exit("Unable to "+command)
    for line in lines:
        IDs.append(line.split()[0])


# Find the duds
duds = []

for id in IDs:
    command = "glite-transfer-status -s "+service+" -l "+id
    lines,errors = runLCG(command)
    if errors:
        sys.exit("Unable to "+command)

    source = ''
    reason = ''

    for line in lines:
        if len(line) > 1:

            if line.split()[0] == 'Source:':
                source = line.split()[1]
                
            if line.split()[0] == 'Reason:':
                reason = ''.join(line)

            if "source file doesn't exist" in reason:
                duds.append(source+'\n')


# Uniqify
duds = list(set(duds))


# Write log file
log_file.writelines(duds)
log_file.close()
