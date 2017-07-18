#!/usr/bin/env python
"""
DumpVerification Data to T1 or T2 sites.
jonathan perkin 20110303

Options: -t --tier   <T1 or T2>
         -p --path   <LFC path>
         -r --repreg <REP or REG> to Replicate or Register
         -f --fts    <0 or 1> 0 = use lcg-rep, 1 = use FTS
Example:
     $./DumpVerification.py 
       -t T1 
       -p /grid/t2k.org/nd280/production004/A/rdp/verify/v9r7p1/ 
       -r REP
       -f 1
"""

import os
import sys
from time import sleep
import ND280GRID
import optparse


def RepReg(repreg):
    if repreg == "REP":
        ## Run SyncDirs.py 
        command="./SyncDirs.py -p '.root' -a "+dirLFC+" -b "+dirSE+" -f "+str(fts)+" -i "+str(n_syncs)+" >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)

    elif repreg == "REG":
        ## Run RegDarkData.py 
        command="./RegDarkData.py -l "+dirLFC+" "+srmlist+" >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)
    

# Parser Options
parser = optparse.OptionParser()
parser.add_option("-t","--tier",  dest="tier",  type="string",help="Specify either dumping to T1 or T2")
parser.add_option("-p","--path",  dest="path",  type="string",help="Path to verification data in LFC, e.g. /grid/t2k.org/nd280/production004/A/mcp/verify/v9r5/neut")
parser.add_option("-r","--repreg",dest="repreg",type="string",help="Specify REP to replicate data, REG to register it")
parser.add_option("-f","--fts",   dest="fts",   type="int",   help="Specify 1 to use FTS 0 to use lcg-cr")
(options,args) = parser.parse_args()


## Use FTS?
fts = options.fts
if not fts:
    fts = 1


## T1 or T2 dumping?
tier = options.tier
if tier == "T1":
    SEs = ['srm-t2k.gridpp.rl.ac.uk',
           't2ksrm.nd280.org']

elif tier == "T2":
    SEs = ['gfe02.grid.hep.ph.ic.ac.uk',
           'se03.esc.qmul.ac.uk',
           'ccsrm02.in2p3.fr',
           'hepgrid11.ph.liv.ac.uk',
           'lcgse0.shef.ac.uk']

else:
    sys.exit("Please specify either T1 or T2 dumping with -t or --tier option")
       
srmlist=''
for se in SEs: srmlist += se+' '


## Verification path
data_path = options.path
if not "verify" in data_path and not "/mcp/" in data_path and not "/rdp/" in data_path:
    sys.exit("Please specify a path to the verification data in the LFC with -p or --path option")


## Replicate or Register
repreg = options.repreg
if not repreg in ["REP","REG"]:
    sys.exit("Please specify -r REP to replicate or -r REG")


## The FTS log directory
transfer_dir= os.getenv("ND280TRANSFERS")
if not transfer_dir:
    transfer_dir=os.getenv("HOME")

## Files to dump
interesting=['numc:','gnmc:','anal:','cali:','cata:','cnfg:','logf:','reco:','unpk:']


## Loop over the SEs in question
for se in SEs:
    ## The SE root directories
    se_root = ND280GRID.GetTopLevelDir(se)

    ## Keep track of multiple synchronisations
    n_syncs = 0

    ## List verification directory
    command = "lfc-ls -R "+data_path
    lines,errors = ND280GRID.runLCG(command)
    
    for line in lines:
        for interest in interesting:
            if interest in line:
                vari_path = ND280GRID.rmNL(line.replace(':',''))
            
                 ## The synchronisation directories
                dirSE  = se_root+vari_path.replace('/grid/t2k.org/','')
                dirLFC = 'lfn:'+vari_path
            
                ## stdout and stderr redirection
                std_out=transfer_dir+'/verification.'+se.split('.')[0]+'.'+str(n_syncs)+'.out';
                std_err=std_out.replace('.out','.err')
                
                ## Replicate or Register
                RepReg(repreg)
                
                ## Wait a second
                n_syncs += 1
                sleep(1)

                
