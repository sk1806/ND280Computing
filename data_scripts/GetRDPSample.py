#!/usr/bin/env python

from random import *
from ND280GRID import *
from GetMCPSample import GetTheFiles
import os
import sys

#os.environ['LCG_GFAL_INFOSYS']='lcg-bdii.cern.ch:2170'

def main():
    # hard coded root to RDP files, not very glamourous
    lfcRoot   = '/grid/t2k.org/nd280/production006/F/rdp'
        
    # get a sample from each directory can modify range and optionally add
    # path to specific file type e.g. anal/
    lfcDirs=[]
    for i in [11]:
        lfcDirs.append('%s/ND280/000%02d000_000%02d999/logf'%(lfcRoot,i,i))

    # lfcDirs=[lfcRoot]
    
    # hard coded root to local dir
    localRoot = '/data1/perkin/t2k'

    # fraction of the total sample to acquire
    fractionToGet=0.01

    # the SE you preferentially want to copy from
    defaultSE='se03.esc.qmul.ac.uk'

    # call function to get the files
    GetTheFiles(lfcDirs,localRoot,fractionToGet,defaultSE)


if __name__=='__main__':
    main()
