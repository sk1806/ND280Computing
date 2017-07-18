#!/usr/bin/env python
"""
Synchronise TRIUMF and RAL with LFC - to be run daily by CRON
jonathan perkin 20110214
"""

import os
import sys
from time import sleep
from ND280GRID import *

## The SE root directories 
triumf_root = GetTopLevelDir('t2ksrm.nd280.org')
ral_root    = GetTopLevelDir('srm-t2k.gridpp.rl.ac.uk')

## Print the disk usage
PrintSESpaceUsage();
    
## Directory in which to write stdout, stderr    
transfer_dir= os.getenv("ND280TRANSFERS")

## Loop over detectors and subdetectors:
DETECTORS = ND280DETECTORS
DETECTORS.append('INGRID')
for detector in DETECTORS:
#    if detector in ['ECAL','SMRD','INGRID','ND280','FGD','TPC']: 
#        continue
    # list of directories to sync
    path_list = []

    if detector=='INGRID':
        path_list.append(GetCurrentRawDataPath(detector,detector))
    else:
        path_list.append(GetCurrentRawDataPath(detector)) 
        
# allow override to check for and recover historic files at KEK    
    if len(sys.argv) == 2:
        if sys.argv[1] == 'RECOVER':
            print 'Checking for and recovering old '+detector+' data...'
            
            command = 'lcg-ls ' + se_roots['kek2-se01.cc.kek.jp'].replace('nd280/','') + path_list[0].rstrip(path_list[0].split('/')[-1])
            lines,errors = runLCG(command)
# only look back at latest 3 directories not including the current one
            lines.sort()
#            lines = lines[-4:-1]
            lines = lines[-2:-1]
            lines     = [l.replace('/t2k.org','') for l in lines]
            path_list = [l for l in lines if l not in path_list]
            
    for data_path in path_list:
         ## The data folder 0000*000_0000*999
        data_folder = data_path.split('/')[-1]

         ## The synchronisation directories, be careful with TRIUMF
        dirRAL = ral_root            +data_path+'/'
        dirTRI = triumf_root         +data_path.replace('nd280/','')+'/'
        dirLFC = 'lfn:/grid/t2k.org' +data_path+'/'

         ## stdout and stderr redirection
        out_ral=transfer_dir+'/'+data_folder+'.'+detector+'.sync.ral.'+str(datetime.now().hour)+'.out';
        out_tri=out_ral.replace('.ral','.tri')
        err_ral=out_ral.replace('.out','.err')
        err_tri=out_tri.replace('.out','.err')

        ## Get PID for unique FTS transfer filenames
        pid = str(os.getpid())

        ## Run SyncDirs.py for RAL
        command="./SyncDirs.py -a "+dirLFC+" -b "+dirRAL+" -f 1 -i "+pid+" >"+out_ral+" 2>"+err_ral+" &"
        print '\n'+command+'\n'
        os.system(command)

        ## Wait a second
        sleep(1)

        ## Run SyncDirs.py for TRIUMF, excluding unecessary sub detectors
        if detector in ['ECAL','P0D','SMRD','INGRID']:
            continue
        else:
            command="./SyncDirs.py -a "+dirLFC+" -b "+dirTRI+" -f 1 -i "+pid+ " >"+out_tri+" 2>"+err_tri+" &"
            print '\n'+command+'\n'
            os.system(command)
