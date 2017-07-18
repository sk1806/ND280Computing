#!/usr/bin/env python


"""
This script creates directories on the LFC and SE's for raw data format. See the option descriptions below for usage.
Should be run with Role=production and not Role=lcgadmin to ensure permissions for the collaboration

"""

import sys
import re
import tempfile
import os
import optparse
import shutil
import stat
import glob
import ND280GRID
import time

#Parser options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("--testfile",help="Some small test file to copy across and delete after", default="test.file")
parser.add_option("--srm",     help="SRM progenitor to create directories with, or all for every SE")
parser.add_option("--version", help="Version of nd280/software processed with")
parser.add_option("--prod",    help="Production, e.g. 4A")
parser.add_option("--type",    help="Production type, rdp,calib add verify for verification, e.g. rdpverify")

#Optional
parser.add_option("--append",  help="Append directory suffix")
parser.add_option("--dirs",    help="Directories to be created")
parser.add_option("--lfc",     help="Create logical files paths? default=1", type="int", default=1)
parser.add_option("--sets",    help="Datasets to be created")
parser.add_option("--debug",   help="Run in debug mode? default=0",          type="int", default=0)

(options,args) = parser.parse_args()

if options.debug:
    print 'RUNNING in DEBUG mode'
###############################################################################

# Main Program

#SRM:s are in the format:
#srm-t2k.gridpp.rl.ac.uk
se_roots = ND280GRID.GetSERoots()
srm      = options.srm
if not srm or not srm in se_roots and not srm == 'all':
    sys.exit('Please state an srm to create directories on:\n'+'\n'.join(se_roots.keys()))


version = options.version
prod    = options.prod
if not version and not prod:
    sys.exit('Please specify software version (e.g. v8r5p9) with --version or production (e.g. 4A) with --prod')
respin=''
prodnr=''
if prod:
    respin=prod[-1]
    prodnr='production'
    nr=prod[:-1]
    if len(nr) == 1:
        prodnr += '00'
    if len(nr) == 2:
        prodnr += '0'
    prodnr += nr

dtype = options.type
if prod and not dtype:
    sys.exit('Please specify production type with -t')

verify = ''
if dtype != 'calib' and len(dtype) > 3:
    dtype = dtype.replace('/','') # slash may or may not be present
    verify = dtype[3:]
    dtype  = dtype[:3]

if verify and (not version or not prod):
    sys.exit("Please specify software version with --version and prod with --prod")

dirlist = []
dirs=options.dirs
if dirs:
    dirlist = dirs.split(',')

setlist = []
sets=options.sets
if sets:
    setlist = sets.split(',')

testfile=options.testfile
if not testfile:
    sys.exit('Please give some small dummy testfile to copy and delete')

lfc=options.lfc
    
rundirs=['00000000_00000999', '00001000_00001999', '00002000_00002999', '00003000_00003999', '00004000_00004999', '00005000_00005999', '00006000_00006999', '00007000_00007999', '00008000_00008999', '00009000_00009999']
if setlist:
    rundirs = setlist

file_types=[]
if dtype == 'rdp':
    file_types = ['unpk','cali','reco','anal','logf','cata','cnfg']
elif dtype == 'fpp':
    file_types = ['unpk','cali','reco','anal','logf','cata','cnfg']
    rundirs    = ['00008000_00008999', '00009000_00009999']
elif dtype == 'calib':
    file_types = ['unpk','cali','cata','logf','stft','cmud']
else:
    print dtype + 'is not a recongnised poduction type!'
    sys.exit()
        
if dirlist:
    file_types = dirlist

suff = options.append
if suff:
    for i,f in enumerate(file_types):
        file_types[i] = f+suff
        print file_types[i]

success = 0
failed  = 0

for this_srm in se_roots:

    se_root = se_roots[this_srm].rstrip('/')

    if srm != 'all' and srm != this_srm:
        continue

    #Do nothing at TRIUMF and kek
    if 'kek2' in this_srm or 't2ksrm' in this_srm:
        print ' I will not make directories in kek or TRIUMF'
        continue
            
    print 'Examining ' + se_root
  
    for rundir in rundirs:
        for file_type in file_types:

            OK = 0
            catalog=''
            if prod and dtype != 'calib':
                if verify:
                    catalog = prodnr + '/' + respin + '/' + dtype + '/' + verify  + '/' + version + '/' + file_type
                else:
                    catalog = prodnr + '/' + respin + '/' + dtype + '/ND280/' + rundir + '/' + file_type
            elif dtype == 'calib':
                catalog = dtype + '/' + version + '/ND280/ND280/' + rundir + '/' + file_type
            else:
                catalog = version + '/' + file_type + '/ND280/ND280/' + rundir

            create_srm = 0
            create_lfn = 0
            
            command = 'lcg-ls ' + se_root + '/' + catalog
            lines,errors=ND280GRID.runLCG(command)
            if errors:
                create_srm = 1
                
            if lfc:
                command = 'lfc-ls /grid/t2k.org/nd280/' + catalog
                lines,errors=ND280GRID.runLCG(command)
                if errors:
                    create_lfn = 1
                
            if create_lfn:

                print 'Creating SRM and LFN directories...'
                command =  'lcg-cr -d ' + se_root + '/' + catalog + '/' + testfile + ' -l lfn:/grid/t2k.org/nd280/' + catalog + '/' + testfile + ' file:' + testfile + '\n'
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)

                command = 'lcg-del -a lfn:/grid/t2k.org/nd280/' + catalog + '/' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)
                    if errors:
                        print 'failed to run ' + command
                    else:
                        OK=1
                        print 'done'

            elif create_srm:

                print 'Creating SRM directory...'
                command = 'lcg-cp file:' + testfile + ' ' + se_root + '/' + catalog + '/' + testfile + '\n'
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)
                command = 'lcg-del -l ' + se_root + '/' + catalog + '/' + testfile + '\n'
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)
                    if errors:
                        print 'failed to run ' + command
                    else:
                        OK = 1
                        print 'done'

            else:
                print 'SRM cleanup'                    
                command = 'lcg-del -l ' + se_root + catalog + '/' + testfile + '\n'
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)
                OK = 1


            if create_lfn and OK:
                print 'Setting LFN permissions'
                command = 'lfc-setacl -m g:t2k.org/Role=production:rwx,m:rwx /grid/t2k.org/nd280/' + catalog
                if options.debug:
                    print command
                else:
                    lines,errors=ND280GRID.runLCG(command)  


            if not OK:
                failed += 1
            else:
                success += 1

        #Only run once for verify
        if verify:
            break

print '---------------------------------'
print 'OK directories:     '+str(success)
print 'Failed directories: '+str(failed)
