#!/usr/bin/env python

### simple wrapper script for RemoveRawData.py that clears KEK SE
### directories

from ND280GRID import *
import os
import sys

KEKSE = 'kek2-se01.cc.kek.jp'

## the FTS log directory
transfer_dir= os.getenv("ND280TRANSFERS")
if not transfer_dir:
    transfer_dir=os.getenv("HOME")

## loop over detectors, include INGRID
DETECTORS = ND280DETECTORS
DETECTORS.append('INGRID')
for detector in DETECTORS:

    # list of directories to sync
    path_list = []
    
    if detector=='INGRID':
        path_list.append(GetCurrentRawDataPath(detector,detector))
    else:
        path_list.append(GetCurrentRawDataPath(detector)) 

        
    # allow override to check for and recover historic files at KEK    
    if len(sys.argv) == 2:
        if sys.argv[1] == 'RECOVER':
            print 'Checking for and cleaning old '+detector+' data...'

            command = 'lcg-ls ' + se_roots['kek2-se01.cc.kek.jp'].replace('nd280/','') + path_list[0].rstrip(path_list[0].split('/')[-1])
            lines,errors = runLCG(command)
            lines     = [l.replace('/t2k.org','') for l in lines]
            path_list = [l for l in lines if l not in path_list]


    for currentDetectorPath in path_list:

        LFCSubDir = 'lfn:/grid/t2k.org'+currentDetectorPath

        ## stdout and stderr redirection
        std_out=transfer_dir+'/cleanKEK'+currentDetectorPath.replace('/','.')+'.out'
        std_err=std_out.replace('.out','.err')
        
        command = "nohup nice ./RemoveRawData.py -l "+LFCSubDir+" -s "+KEKSE+" >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)
