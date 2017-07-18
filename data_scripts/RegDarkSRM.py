#!/usr/bin/env python

"""

Sometimes small numbers of dark files are present in SE directories,
such directories being identified by the archiving/cleanup scripts.
Use this quick and dirty script to register these dark files.

jonathan perkin 20120217

"""

from ND280GRID import *
import optparse
import sys


# Parser Options
parser = optparse.OptionParser()
parser.add_option("-s","--srmdir",dest="srmdir",type="string",help="srm directory to register dark data from")
(options,args) = parser.parse_args()

if not options.srmdir:
    parser.print_help()
    sys.exit(1)

srmdir = options.srmdir.rstrip('/')
    
# Get the list of files in this directory - try and avoid limitations of lcg-ls
files  = []
nLines = 999
offset = 0

while 1:
    command = 'lcg-ls -c %d -o %d %s' % (nLines,offset,srmdir)
    lines,errors = runLCG(command,in_timeout=3600)

    # break out when end of listing has been reached
    if not lines : break
    if lines[0].rstrip('/').split('/')[-1] == srmdir.rstrip('/').split('/')[-1] : break

    files  += [rmNL(line.split('/')[-1]) for line in lines]
    offset += nLines


# Get corresponding lfc path
srmroot = se_roots[GetSEFromSRM(srmdir)]

# Just in case the dark data isn't in the nd280 folder, truncate it from the SR root directory
if not 'nd280/' in srmdir : 
    srmroot = srmroot.rstrip('nd280/')

# Formulate the logical file path
lfcdir = 'lfn:/grid/t2k.org/nd280'+srmdir.replace(srmroot,'')
lfcdir = lfcdir.rstrip('/')

# Register them
for file in files:
    
    # does a GUID already exist?
    command = 'lcg-lg '+lfcdir+'/'+file
    lines,errors = runLCG(command,in_timeout=3600)

    if lines:
        guid = rmNL(lines[0])
        command = 'lcg-rf -g '+guid+' '+srmdir+'/'+file
        lines,errors = runLCG(command)

    else:
        command = 'lcg-rf -l '+lfcdir+'/'+file+' '+srmdir+'/'+file
        lines,errors = runLCG(command)

    if errors: print errors
    
