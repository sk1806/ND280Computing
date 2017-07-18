#!/usr/bin/env python
"""
Register Current Raw Data Files on TRIUMF and RAL - to be ran 4 x daily by CRON
jonathan perkin 20110214
"""

import os
import sys
from ND280GRID import *

## The T1 SEs
SEs=['t2ksrm.nd280.org','srm-t2k.gridpp.rl.ac.uk']

## The logging folder
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
            # only look back at latest 3 directories
            lines.sort()
            lines = lines[-2:-1]
            lines     = [l.replace('/t2k.org','') for l in lines]
            path_list = [l for l in lines if l not in path_list]

    for data_path in path_list:

        ## The data folder 0000*000_0000*999
        data_folder = data_path.split('/')[-1]

        ## The full LFC current raw data path
        dir = '/grid/t2k.org'+data_path+'/'

        ## stdout and stderr redirection
        out_file=transfer_dir+'/'+data_folder+'.'+detector+'.T1.reg.'+str(datetime.now().hour)+'.out'
        err_file=out_file.replace('.out','.err')

        ## Which SRMs?
        srmlist=''
        for se in SEs:
            if (not detector in ['ECAL','P0D','SMRD', 'INGRID'] and 't2ksrm' in se) or 'srm-t2k' in se:
                srmlist += se+' '

        ## Run RegDarkData.py
        command="./RegDarkData.py -l lfn:"+dir+" "+srmlist+" >"+out_file+" 2>"+err_file+" &"
        print command
        os.system(command)
