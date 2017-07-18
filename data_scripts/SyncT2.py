#!/usr/bin/env python
"""
Synchronise T2 sites with LFC - to be run daily by CRON
jonathan perkin 20110214
"""

import os
import sys
from time import sleep
from ND280GRID import *

## The list of T2 sites
SEs = ['gfe02.grid.hep.ph.ic.ac.uk',
       'se03.esc.qmul.ac.uk',
       'hepgrid11.ph.liv.ac.uk',
       'ccsrm02.in2p3.fr',
       'lcgse0.shef.ac.uk',
       't2se01.physics.ox.ac.uk'] #',
#       'fal-pygrid-30.lancs.ac.uk']


## The data folder 0000*000_0000*999
data_folder = GetCurrentRawDataFolder()

## The raw data path /nd280/raw/ND280/ND280/0000*000_0000*999
data_path   = GetCurrentRawDataPath()


## Print the disk usage
PrintSESpaceUsage();
 
    
## The FTS log directory
transfer_dir= os.getenv("ND280TRANSFERS")

for se in SEs:
    ## The SE root directories
    se_root = GetTopLevelDir(se)
    
    ## The synchronisation directories
    dirSE  = se_root+data_path+'/'
    dirLFC = 'lfn://grid/t2k.org'+data_path+'/'

    ## stdout and stderr redirection
    std_out=transfer_dir+'/'+data_folder+'.sync.'+se.split('.')[0]+'.'+str(datetime.now().hour)+'.out';
    std_err=std_out.replace('.out','.err')
    
    ## Get PID for unique FTS transfer filenames
    pid = str(os.getpid())
    
    ## Run SyncDirs.py
    command="./SyncDirs.py -p GOODFILES -a "+dirLFC+" -b "+dirSE+" -f 1 -i "+pid+" >"+std_out+" 2>"+std_err+" &"
    print command
    os.system(command)

    ## Wait a second
    sleep(1)
