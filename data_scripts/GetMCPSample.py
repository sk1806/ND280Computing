#!/usr/bin/env python

from random import *
from ND280GRID import *
import os
import sys
import traceback

#os.environ['LCG_GFAL_INFOSYS']='lcg-bdii.cern.ch:2170'

# define a function to get the files
def GetTheFiles(lfcDirs,localRoot,fractionToGet,defaultSE):
  
    # list of files to copy
    fileList = []

    # loop over directories
    for lfcDir in lfcDirs:

        # generate a list of the file paths in the given LFC directory
        command = 'lfc-ls '+lfcDir
        lines,errors = runLCG(command)

        # full file names
        files = [ 'lfn:'+lfcDir+'/'+f for f in lines ]
        print files

        # randomly sample a fraction the file paths if desired
        if fractionToGet<1:
            fileList += sample(files,int(len(files)*fractionToGet))
        else:
            fileList += files

    # get the files
    LocalCopyLFNList(fileList,localRoot,defaultSE)


def main():
    # hard coded roots to MCP files
    lfcDirs = ['/grid/t2k.org/nd280/production006/B/mcp/neut/2010-11-air/magnet/run2/flatv1r11',
               '/grid/t2k.org/nd280/production006/B/mcp/neut/2010-11-air/magnet/run3/flatv1r11',
               '/grid/t2k.org/nd280/production006/B/mcp/neut/2010-11-air/magnet/run4/flatv1r11']

    # hard coded root to local dir
    localRoot = '/data/perkin/t2k'
    
    # fraction of the total sample to acquire
    fractionToGet=1
    
    # the SE you preferentially want to copy from
    defaultSE='srm-t2k.gridpp.rl.ac.uk'
    
    # call function to get the files
    GetTheFiles(lfcDirs,localRoot,fractionToGet,defaultSE)


if __name__=='__main__':
    main()
