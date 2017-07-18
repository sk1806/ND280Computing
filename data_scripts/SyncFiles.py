#!/usr/bin/env python

"""
A simple wrapper script for CopySRM() that is intended to be implemented as a subprocess
by other archiving tools
"""

from ND280GRID import *
import optparse
import os
import sys
import time
import traceback

# Parser Options

parser = optparse.OptionParser()
## Common with genie_setup
parser.add_option("--srm",      help="SE to which files will be copied", default='')
parser.add_option("--fts",      help="Use FTS flag 1=yes 0=no", type="int", default=1)
parser.add_option("--ftsInt",   help="Optional integer to pass to FTS for uniquifying transfer-file names", default='')
parser.add_option("--filelist", help="File containing list of specific LFNs to sync", default='')

(options,args) = parser.parse_args()

###############################################################################

# The start time.
start = time.time()

# Make sure filelist was provided
if not options.filelist:
    sys.exit('Please specify input file list!')
    parser.print_help()


# Use FTS?
fts=options.fts


# Add optional integer to FTS transfer-file name (to prevent overwriting)
ftsInt=options.ftsInt
if not ftsInt:
    ftsInt=os.getpid()

# Which SRM?
srm = options.srm

# Read LFNs
f = open(options.filelist,'r')
filelist = f.readlines()
f.close()

# Remove blank lines
for f in filelist[:]:
    if not f.strip():
        filelist.remove(f)

# Keep track of last file
lastfile     = filelist[-1]
isLastFile = False

# read the file list
for lfn in filelist:
    
    # Is this last file? Need to keep track for initiating FTS transfers...
    if lfn == lastfile:
        isLastFile = True
    try:
        # Create file instance and copy to desired SE
        f = ND280File(lfn,check=False)
        f.CopySRM(srm, fts, isLastFile, ftsInt)

    except:
        traceback.print_exc()

# The time taken
duration = time.time() - start

print 'It took '+str(duration)+' seconds to synchronise files.\n'
