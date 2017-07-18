#!/usr/bin/env python

"""
For a given LFC directory, containing run/subrun data - create an appropriate set of inputs for hadding
RDP should generally hadd all subruns to a single run
MCP must take into consideration the hadded file size - default to <~ 1GB 
"""

import argparse
import os
import sys
import commands
import ND280GRID

# parse arguments
parser = argparse.ArgumentParser()

parser.add_argument('lfcdir',                 help='LFC directory containing data to hadd'          )
parser.add_argument('--prefix',               help='Optionally override the output file name prefix')
parser.add_argument('--maxMB',  default=1024, help='max no. of MB for hadded output'                )
args = parser.parse_args()

# going to write one output file per list of files to hadd
# define a filename prefix
if args.prefix:
    prefix = str(args.prefix)
else:
    prefix = args.lfcdir.lstrip('/').rstrip('/').replace('/','.')

outProj = 'lfn:' + os.getenv('LFC_HOME')


# method for writing an output file list
def WriteOutFile(tag,outlines) : 
    print 'Writing hadd list file for %s' % (tag)
    open('%s.hadd.%s'% (prefix,tag),'w').writelines(outlines)


# method for writing an output file path to the list of output lines, returns run and subrun
# assumes files observe the official naming format, script will barf if not
def WriteRunLine(name,outlines) : 
    run,subrun = name.split('_')[3].split('-')
    outlines.append(outProj+'/'+args.lfcdir+'/'+name+'\n')
    return run,subrun
    
    
# write output lines on the fly
outlines = [] 

# does lfcdir point to RDP?
if '/rdp/' in str(args.lfcdir):
    print 'Reading RDP - hadding subruns into runs'
    names,errors = ND280GRID.runLCG('lfc-ls %s' % args.lfcdir)    
    thisRun      = '' # track the run number
    
    for n in names:
        run,subrun = WriteRunLine(n,outlines)
        
        # the run number changed for the first time
        if thisRun != run and thisRun == '':
            thisRun = run
            continue

        # the run number changed some subsequent time
        if thisRun != run:
            WriteOutFile(thisRun,outlines[:-1]) # write the outfile for the previous run
            outlines = outlines[-1:]            # reset outlines
            thisRun  = run                      # increment run
    
    # end of loop over names - write the last run
    WriteOutFile(thisRun,outlines)

else:
    print 'hadding files upto <~%d MB'%(args.maxMB)
    # long list the directory - want to parse file sizes and max out appropriately
    # (don't create ND280Dir as instantiating an ND280File object for each file is too slow)
    lines,errors = ND280GRID.runLCG('lfc-ls -l %s' % args.lfcdir)
    totalSize    = 0 # track the output size in MB
    iOut         = 0 # index

    for l in lines:
        n               = l.split()[-1]
        thisRun,subrun  = WriteRunLine(n,outlines)
        size            = int(l.split()[4])/(1024*1024) # size in MB 
        totalSize      += size

        # the run number changed some subsequent time
        if totalSize >= args.maxMB:
            WriteOutFile('%08d'%iOut,outlines[:-1]) # write the outfile
            totalSize = size                        # reset totalSize
            outlines  = outlines[-1:]               # reset outlines
            iOut     += 1                           # increment counter
    
    # end of loop over names - write the remaining files
    WriteOutFile('%08d'%iOut,outlines)
    
    

                 

                    



 

