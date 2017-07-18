#!/usr/bin/env python
"""
Register ALL Files on TRIUMF and RAL - to be ran daily by CRON

"""

import os
import sys
import optparse
from ND280GRID import *

# Parser Options:
parser = optparse.OptionParser(usage ="""\
usage: %prog [options]

       Register ALL Files on TRIUMF and RAL - to be ran daily by CRON

       Registers files in all subdirectories of /grid/t2k.org/nd280/raw/ND280/
       on T1 SEs unless overridden by optional SE list
       

Examples:
       To register the contents of /grid/t2k.org/nd280/raw/ND280/* in T1
       (default)
            $./RegAll.py

       To register the contents of /grid/t2k.org/nd280/raw/ND280/ND280 on
       srm-t2k.gridpp.rl.ac.uk
            $./RegAll.py --se=srm-t2k.gridpp.rl.ac.uk --detectors=ND280
       """)
parser.add_option("--se",        type="string", default='',help="'/' delimited list of SEs on which to register dark data")
parser.add_option("--detectors", type="string", default='',help="'/' delimited list of subdetectors directories in which to register dark data")
(options,args) = parser.parse_args()

## SEs
if options.se:
    ## Parse optional list of SEs
    SEs=[]
    for se in options.se.split('/'):
        SEs.append(se)
else:
    ## The T1 SEs
    SEs=['t2ksrm.nd280.org','srm-t2k.gridpp.rl.ac.uk']

## Subdetectors
if options.detectors:
    ## Parse optional list of SEs
    sub_detectors=[]
    for sub in options.detectors.split('/'):
        sub_detectors.append(sub)
else:
    sub_detectors = DETECTORS


## The logging folder
transfer_dir= os.getenv("ND280TRANSFERS")

## The data root
data_root = '/grid/t2k.org/nd280/raw/ND280'

## Loop over detectors and subdetectors:
for detector in sub_detectors:

    ## Get list of all data folders
    command = 'lfc-ls '+data_root+'/'+detector
    lines,errors = runLCG(command)

    for data_folder in lines:
    
        ## The full LFC current raw data path
        dir = data_root+'/'+detector+'/'+data_folder
        
        ## stdout and stderr redirection
        out_file=transfer_dir+'/'+data_folder+'.'+detector
        if not options.se:
            out_file+='.ALL.T1.reg.'+str(datetime.now().hour)+'.out'
        else:
            out_file+='.ALL.'+options.se.replace('/','.')+'.reg.'+str(datetime.now().hour)+'.out'
        err_file=out_file.replace('.out','.err')
            
        ## Which SRMs?
        srmlist=''
        for se in SEs:
            if not options.se and not options.detectors:
                if (not detector in ['ECAL','P0D','SMRD'] and 't2ksrm' in se) or 'srm-t2k' in se:
                    srmlist += se+' '            
            else:
              srmlist += se+' '  
                

        ## Run RegDarkData.py
        command="./RegDarkData.py -l lfn:"+dir+" "+srmlist+" >"+out_file+" 2>"+err_file+" &"
        print command
        os.system(command)
