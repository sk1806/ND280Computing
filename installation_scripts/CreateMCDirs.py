#!/usr/bin/env python


"""
This script creates directories on the LFC and SE's for MC format. See the option descriptions below for usage.
Should be run with Role=production and not Role=lcgadmin to ensure permissions for the collaboration
F.Dufour October 2011
Standard command:
python CreateMCDirs.py  -p 4Z -t mcp -m genie -c basket -r 2010-02-water  -s all -l 1 -f dummy.txt
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
parser.add_option("--testfile", help="Some (not too) small test file to copy across and delete after", default="test.file")
parser.add_option("--srm",      help="srm progenitor to create directories with, or all for every SE")
parser.add_option("--version",  help="version of nd280/software processed with")
parser.add_option("--prod",     help="Production, e.g. 4A")
parser.add_option("--type",     help="Production type, mcp, add verify for verification, e.g. mcp/verify")
parser.add_option("--generator",help="MC event generator: genie or neut")
parser.add_option("--geometry", help="Type of beam and water in or out: 2010-02-water, 2010-11-air, 2010-11-water")
parser.add_option("--vertex",   help="Vertex region: magnet or basket")

#Optional
parser.add_option("--append",   help="Append directory suffix")
parser.add_option("--dirs",     help="Directories to be created")
parser.add_option("--lfc",      help="Create logical file paths? default=1", type="int", default=1)
parser.add_option("--debug",    help="Run in debug mode? default=0",         type="int", default=0)

(options,args) = parser.parse_args()

if options.debug:
    print 'RUNNING in DEBUG mode'
###############################################################################

# Main Program

#SRM:s are in the format:
se_roots = ND280GRID.GetSERoots()
srm=options.srm
if srm not in se_roots.keys() and srm != 'all':
    sys.exit('Please state an srm to create directories on:\n'+'\n'.join(se_roots.keys()))


version = options.version
prod     = options.prod
if not version and not prod:
    parser.print_help()
    sys.exit('Please specify software version (e.g. v8r5p9) with --version and production (e.g. 4A) with --prod')
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
    parser.print_help()
    sys.exit('Please specify production type with --type')

verify = ''
if len(dtype) > 3:
    dtype = dtype.replace('/','') # slash may or may not be present
    verify = dtype[3:]
    dtype  = dtype[:3]

generator = options.generator
if not generator:
    parser.print_help()
    sys.exit("Please specify MC type (genie or neut) with --generator")

geometry = options.geometry
if not geometry:
    parser.print_help()
    sys.exit("Please specify Geometry configuration (2010-02-water, 2010-11-air or 2010-11-water) with --geometry")

vertex = options.vertex
if not vertex:
    parser.print_help()
    sys.exit("Please specify vertex region (magnet or basket) with --vertex flag")

dirlist = []
dirs=options.dirs
if dirs:
    dirlist = dirs.split(',')

testfile=options.testfile
if not os.path.exists(testfile):
    sys.exit('Please give some small dummy testfile to copy and delete')

lfc=options.lfc

mcsubtypes=[]
if vertex == 'magnet' and geometry == '2010-02-water':
    mcsubtypes=['beama']
if vertex == 'magnet' and (geometry == '2010-11-water' or geometry == '2010-11-air') :
    mcsubtypes=['beamb','beamc']
if vertex == 'basket':
    mcsubtypes=['beam','ccpiplus','ccpizero','ncpiplus','ncpizero','nue']

print mcsubtypes
    
file_types=[]
if dtype == 'mcp' and generator == 'neut':
    file_types=['numc','cali','reco','anal','logf','cata','cnfg','elmc','g4mc']
if dtype == 'mcp' and generator == 'genie':
    file_types=['gnmc','numc','cali','reco','anal','logf','cata','cnfg','elmc','g4mc']

if dirlist:
    file_types = dirlist

suff=options.append
if suff:
    for i,f in enumerate(file_types):
        file_types[i] = f+suff
        print file_types[i]

success = 0
failed  = 0

for this_site in se_roots:

    this_srm = se_roots[this_site].rstrip('/')
    
    if srm != 'all' and srm != this_site:
        continue

    #Do nothing at TRIUMF and kek
    if 'kek2' in this_site or 't2ksrm' in this_site:
        print ' I will not make directories in kek or TRIUMF'
        continue

    print 'Examining ' + this_srm

    for mcsubtype in mcsubtypes:
        for file_type in file_types:

            OK = 0
            catalog=''
            if prod:
                if verify:
                    catalog = prodnr + '/' + respin + '/' + dtype + '/' + verify  + '/' + version + '/' + generator + '/' + geometry + '/' + vertex + '/'+ mcsubtype + '/' + file_type
                else:
                    catalog = prodnr + '/' + respin + '/' + dtype + '/' + generator + '/' + geometry + '/' + vertex + '/'+ mcsubtype + '/' + file_type
            else:
                # Not up to date. Make sure to create the structure that you want
                catalog = version + '/' + file_type + '/ND280/ND280/' + rundir
            
            create_srm = 0
            create_lfn = 0

            command = 'lcg-ls ' + this_srm + '/' + catalog
            lines,errors = ND280GRID.runLCG(command)
            if errors:
                create_srm = 1
            
            if lfc:
                command = 'lfc-ls /grid/t2k.org/nd280/' + catalog
                lines,errors = ND280GRID.runLCG(command)
                if errors:
                    create_lfn = 1
                            
            if create_lfn:
                        
                print 'Creating SRM and LFN directories...'
                command =  'lcg-cr -d ' + this_srm + '/' + catalog + '/' + testfile + ' -l lfn:/grid/t2k.org/nd280/' + catalog + '/' + testfile + ' file:' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)
                command = 'lcg-del -a lfn:/grid/t2k.org/nd280/' + catalog + '/' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)
                    if errors:
                        print 'failed to run ' + command
                    else:
                        OK = 1
                        print 'done'
                
            elif create_srm:
            
                print 'Creating SRM directory...'
                command = 'lcg-cp file:' + testfile + ' ' + this_srm + '/' + catalog + '/' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)
                command = 'lcg-del -l ' + this_srm + catalog + '/' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)
                    if errors:
                        print 'failed to run ' + command
                    else:
                        OK = 1
                        print 'done'
                                
            else:
                print 'SRM cleanup'                    
                command = 'lcg-del -l ' + this_srm + catalog + '/' + testfile
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)
                    OK = 1
                                
            
            if create_lfn and OK:
                print 'Setting LFN permissions'
                command = 'lfc-setacl -m g:t2k.org/Role=production:rwx,m:rwx /grid/t2k.org/nd280/' + catalog
                if options.debug:
                    print command
                else:
                    lines,errors = ND280GRID.runLCG(command)  
            
                
            if not OK:
                failed += 1
            else:
                success += 1
                
        
print '---------------------------------'
print 'OK directories:     '+str(success)
print 'Failed directories: '+str(failed)
        
