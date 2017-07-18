#!/usr/bin/env python
"""
Dump Processed Data to T1 or T2 sites.
jonathan perkin 20110303

Options: -t --tier   <T1 or T2>
         -p --path   <LFC path>
         -r --repreg <REP or REG> to Replicate or Register
         -f --fts    <0 or 1> 0 = use lcg-rep, 1 = use FTS
Examples:
     $./DumpProcessed.py 
       -t T1 
       -p /grid/t2k.org/nd280/production004/A/rdp/ND280/00006000_00006999
       -r REP
       -f 1

     $./DumpProcessed.py 
       -t T2 
       -p /grid/t2k.org/nd280/production004/A/mcp/neut
       -r REP
       -f 0 
"""

import os
import sys
from time import sleep
import ND280GRID
import optparse

# Parser Options
parser = optparse.OptionParser()
parser.add_option("-t","--tier",  type="string",help="Specify either dumping to T1 or T2 or an individual srm")
parser.add_option("-p","--path",  type="string",help="Path to processed data in LFC, e.g. /grid/t2k.org/nd280/production004/A/mcp/verify/v9r5/neut")
parser.add_option("-r","--repreg",type="string",help="Specify REP to replicate data, REG to register it")
parser.add_option("-f","--fts",   type="int",   help="Specify 1 to use FTS 0 to use lcg-cr")
parser.add_option("--filetags",   type="string",help="'/' delimited list of all file tags to archive/clean e.g. reco/cali/anal")
parser.add_option("--pattern",    type="string",help="Only sync files containing <pattern> (default=\'.root\')",default='.root')
(options,args) = parser.parse_args()


## Replicate or Register?
repreg = options.repreg
if not repreg in ["REP","REG"]:
    sys.exit("Please specify -r REP to replicate or -r REG")


## Use FTS?
fts = options.fts
if not fts:
    fts = 1
    
    
## T1 or T2 dumping?
tier = options.tier
if tier == "T1":
    SEs = ['srm-t2k.gridpp.rl.ac.uk']
    
elif tier == "T2":
    SEs = ['se03.esc.qmul.ac.uk',      
           'gfe02.grid.hep.ph.ic.ac.uk',
           'hepgrid11.ph.liv.ac.uk',   
           'lcgse0.shef.ac.uk',        
           't2se01.physics.ox.ac.uk',
           'fal-pygrid-30.lancs.ac.uk']
else:
    SEs = [tier]
    if not tier in ND280GRID.se_roots:
        sys.exit("Please specify either T1 or T2 dumping or specific srm with -t or --tier option")
       
srmlist=''
for se in SEs: srmlist += se+' '


## Processed path
data_path = options.path
if not "/mcp" in data_path and not "/rdp" in data_path and not "/fpp" in data_path:
    sys.exit("Please specify a path to the processed data in the LFC with -p or --path option")
data_path.rstrip('/')


## The FTS log directory
transfer_dir= os.getenv("ND280TRANSFERS")
if not transfer_dir:
    transfer_dir=os.getenv("HOME")


## Files we're interested in
interesting=[]
if options.filetags:
    for tag in options.filetags.split('/'):
        interesting.append(tag+':')
else:
    interesting=['g4mc:','gnmc:','numc:','nucp:','anal:','cali:','cata:','logf:','reco:'] ##,'air:','water:']


## Pattern match?
pattern = options.pattern


## The replicate or register method
def Dump(repreg,se=''):
    ## mcp and rdp directory structures are a bit different
    command = "lfc-ls -R "+data_path
    lines,errors = ND280GRID.runLCG(in_command=command,in_timeout=1800,is_pexpect=False)

    n_files = 0
        
    for line in lines:
        for interest in interesting:
            if interest in line:
                vari_path = ND280GRID.rmNL(line.replace(':','/'))
                dirLFC    = 'lfn:'+vari_path
                
                ## stdout and stderr redirection
                std_out=transfer_dir+'/processed'
                if se: 
                    std_out += '.'+se.split('.')[0]
                std_out += data_path.replace('/grid/t2k.org/nd280','').replace('/','.')+'.'+str(n_files)+'.'+repreg.lower()+'.out';
                std_err=std_out.replace('.out','.err')
                
                ## Replicate or Register?
                if repreg == "REP":

                    ## The SE root directories
                    se_root = ND280GRID.GetTopLevelDir(se)
                    
                    
                    ## The synchronisation directories
                    dirSE  = se_root+vari_path.replace('/grid/t2k.org/','')
                    
                    ## Run SyncDirs.py (nicely)
                    command="nohup nice ./SyncDirs.py --pattern="+pattern+" -a "+dirLFC+" -b "+dirSE+" -f "+str(fts)+" -i "+str(n_files)+" >"+std_out+" 2>"+std_err+" &"

                    print command
                    os.system(command)
                    
                elif repreg == "REG":
                    ## Run RegDarkData.py (nicely)
                    command="nohup nice ./RegDarkData.py -l "+dirLFC+" "+srmlist+" >"+std_out+" 2>"+std_err+" &"
                    print command
                    os.system(command)
                     
                ## Wait a second
                n_files += 1
                sleep(1)


## Replication? - Loop over the SEs in question
if repreg == "REP":
    for se in SEs:
        ## Replicate
        Dump(repreg,se)

## Registration? - Register all SEs in unison
elif repreg == "REG":
    ## Register
    Dump(repreg)


