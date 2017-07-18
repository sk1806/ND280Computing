#!/usr/bin/env python
"""
Replicate or Register list of LFNs to T1 or T2 sites.

Options:--tier      <T1 or T2>
        --repreg    <REP or REG> to Replicate or Register
        --fts       <0 or 1> 0 = use lcg-rep (default), 1 = use FTS
        --filelist  <filename> file contianing list of LFNs to copy

Example incorporating FTS transfer, 24hr wait and dark data registration:
     ./DumpFiles.py --tier=T2 --filelist=sync.list --fts=1 --repreg=REP; sleep 1d; ./DumpFiles.py --tier=T2 --filelist=sync.list --repreg=REG
       
"""

import os
import sys
from time import sleep
import ND280GRID
import optparse

# Parser Options
parser = optparse.OptionParser()
parser.add_option("--tier",    type="string",help="Specify either dumping to T1 or T2 or an individual srm")
parser.add_option("--repreg",  type="string",help="Specify REP to replicate data, REG to register it")
parser.add_option("--fts",     type="int",   help="Specify 1 to use FTS 0 to use lcg-cr", default=1)
parser.add_option("--filelist",type="string",help="File containing list of specific LFNs to sync")
parser.add_option("--uselogname",            help="Use the filelist name in the log file", default=False)
(options,args) = parser.parse_args()


## Replicate or Register?
repreg = options.repreg
if not repreg in ["REP","REG"]:
    sys.exit("Please specify -r REP to replicate or -r REG")


## T1 or T2 dumping?
tier = options.tier
if tier == "T1":
    SEs = ['srm-t2k.gridpp.rl.ac.uk',
           't2ksrm.nd280.org']
    
elif tier == "T2":
    SEs = ['se03.esc.qmul.ac.uk',      
           'gfe02.grid.hep.ph.ic.ac.uk',
           #'hepgrid11.ph.liv.ac.uk',   
           'lcgse0.shef.ac.uk',        
           #'ccsrm02.in2p3.fr',
           't2se01.physics.ox.ac.uk',
           'fal-pygrid-30.lancs.ac.uk']
else:
    SEs = [tier]
    if not tier in ND280GRID.se_roots:
        sys.exit("Please specify either T1 or T2 dumping or specific srm with -t or --tier option")
       
srmlist=''
for se in SEs: srmlist += se+' '


## The FTS log directory
transfer_dir= os.getenv("ND280TRANSFERS")
if not transfer_dir:
    transfer_dir=os.getenv("HOME")


## The file containing the list of LFNs
filelist = options.filelist


## The replicate or register method
def Dump(repreg,data_path='',se=''):

    ## stdout and stderr redirection
    std_out=transfer_dir+'/files'
    if se: 
        std_out += '.'+se.split('.')[0]
    std_out += data_path +'.'+repreg.lower()
    if options.uselogname:
        std_out += '.'+filelist
    std_out += '.out';
    std_err=std_out.replace('.out','.err')
                
    ## Replicate or Register?
    if repreg == "REP":
        
        ## Run SyncFiles.py (nicely)
        command="nohup nice ./SyncFiles.py  --filelist="+filelist+" --srm="+se+" --fts="+str(options.fts)+" >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)
                    
    elif repreg == "REG":

        ## Run RegDarkData.py (nicely)
        command="nohup nice ./RegDarkData.py --filelist="+filelist+" "+srmlist+" >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)



## Peak at the first LFN
lines,errors = ND280GRID.runLCG('head -1 '+filelist,is_pexpect=False)
data_path = '.'.join(lines[0].replace('lfn:/grid/t2k.org/nd280','').split('/')[:-1])

## Replication? - Loop over the SEs in question
if repreg == "REP":
    for se in SEs:
        ## Replicate
        Dump(repreg,data_path,se)

## Registration? - Register all SEs in unison
elif repreg == "REG":
    ## Register
    Dump(repreg,data_path)


