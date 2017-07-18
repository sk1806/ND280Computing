#!/usr/bin/env python

"""
Given a cvmfsAccessList (which may or may not be derived dynamically) file, create a replica of
$LFC_HOME/cvmfsAccessList at each CE such that WMS resource matching will result in delegation
to the given CE

N.B. this only impacts upon jobs for which the InputFile is /cvmfs or locally resident
(hence the DataRequirements point to $LFC_HOME/cvmfsAccessList rather than the actual input)

"""

import argparse
import os
import sys
import ND280GRID

# parse arguments
parser = argparse.ArgumentParser()

parser.add_argument('listpath', help='path to cvmfsAccessList')
args = parser.parse_args()


# check if cvmfsAccessList exists
if not os.path.exists(args.listpath):
    print 'Unable to locate %s' % args.listpath
    sys.exit(1)

# instantiate the local file
f = ND280GRID.ND280File(args.listpath)

# read the ce list
CEs = [ l.strip().split(':')[0] for l in open(args.listpath).readlines() ]

# make sure the file doesn't already exist in LFC
print 'Checking if replica of %s exists in LFC...' % (args.listpath)
try:
    replica = ND280GRID.ND280File('lfn:'+os.getenv('LFC_HOME')+'/'+args.listpath) 
    print 'Yep...'
    isRegistered = True
    f            = replica
except:
    print 'Nope...'
    isRegistered = False

# create a replica for each CE 
for ce in CEs:

    # need to match CE to SE
    for srm in ND280GRID.se_roots:
        if '.'.join(srm.split('.')[1:]) in ce:

            if not isRegistered:
                f.Register(os.getenv('LFC_HOME'),srm)
                isRegistered = True
                f            = ND280GRID.ND280File('lfn:'+os.getenv('LFC_HOME')+'/'+args.listpath) 

            else:
                try:
                    f.CopySRM(srm,use_fts=False)
                except:
                    pass

sys.exit(0)

