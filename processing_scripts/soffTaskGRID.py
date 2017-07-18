#!/usr/bin/env python 

#Example executable file to be submitted with RunCustom.py

import sys
import optparse
import os
import ND280Job
import ND280GRID
from ND280GRID import ND280File
from ND280Job import ND280Process
import random
import time

# Parser Options

parser = optparse.OptionParser()

parser.add_option("-i","--input",dest="input",type="string",help="Input to process, must be an lfn")
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to use")

(options,args) = parser.parse_args()

###############################################################################

# Main Program 

nd280ver=options.version
if not nd280ver:
    sys.exit('Please enter a version of the ND280 Software to use')

input=options.input
if not input and not 'lfn:' in input:
    sys.exit('Please enter an lfn: input file')

input=input.replace("'","")

os.system('env')

#Delay processing by random time
#to avoid database blocking
rt=200*random.random()
print 'Sleeping ' + str(rt) + ' seconds'
time.sleep(rt)

## Job settings
print 'Settings'
## LFC environment variables
os.environ["LFC_HOST"]="lfc.gridpp.rl.ac.uk"

## Use GRIDFTD 2 
os.environ["GLOBUS_FTP_CLIENT_GRIDFTP2"]='true'

## BDII
if not os.getenv("LCG_GFAL_INFOSYS"):
    os.environ["LCG_GFAL_INFOSYS"]='lcg-bdii.gridpp.ac.uk:2170'

fmem=20*1024*1024 #max 20GB file size
vmem=4*1024*1024  #max 4GB memory
base=os.getenv('PWD')
t2ksoftdir=ND280GRID.GetT2KSoftDir()
instDir=t2ksoftdir + '/nd280' + nd280ver + '/'
cmtSetupScr=instDir + '/CMT/setup.sh'
srm=ND280GRID.GetDefaultSE()

#Get input file
print 'Getting input file'
iar=input.split('/')
localfile=iar[-1]
set=localfile[14]
lfn='lfn:/grid/t2k.org/nd280/'+nd280ver+'/soff/ND280/ND280/0000'+str(set)+'000_0000'+str(set)+'999'

outfile=localfile.replace('oa_nd','dq-tpc-bc')

filetorun=base+'/'+localfile

#Site name
site_name=os.getenv("SITE_NAME")
if not site_name:
    raise self.Error('Cannot get the env variable SITE_NAME: On a GRID node? No=Don\'t Worry, yes=WTF')
print 'site name ' + site_name

#If we are at QMUL then get the turl of the local copy of the file
if "QMUL" in site_name:
    #Get replicas
    reps=[]
    command="lcg-lr --vo t2k.org " + input
    lines,errors=ND280GRID.runLCG(command)
    if not errors:
        for l in lines:
            reps.append(l.replace('\n',''))

    srmname = ''
    for r in reps:
        if 'qmul.ac.uk' in r:
            srmname=r

        if not srmname:
            raise self.Error('Could not find file registered at QMUL')

        print 'srm name ' + srmname        
        command="lcg-gt " + srmname + " file"
        lines,errors=ND280GRID.runLCG(command)
        if errors:
            raise self.Error('Could not get file turl',errors)
        file_turl=lines[0].replace('\n','')
        file_turl=file_turl[7:] #remove the preceeding file://
        print 'TURL: ' + file_turl
        filetorun = file_turl

else:
    #Copy from LFN
    command='lcg-cp ' + input + ' ' + filetorun
    lines,errors=ND280GRID.runLCG(command)
    if errors:
        sys.exit('Could not copy file from LFC')
    
## Run the Job
print 'Running job'

command=''
if os.path.isfile(cmtSetupScr):
    command += 'source ' + cmtSetupScr + '\n'
else:
    sys.exit('Could not find the setup script ' + cmtSetupScr)

gblSetupScr=instDir + 'setup.sh'
if os.path.isfile(gblSetupScr):
    command += 'source ' + gblSetupScr + '\n'
else:
    sys.exit('Could not find the setup script ' + gblSetupScr)

os.system('cd '+base)

command+='echo CMTPATH is $CMTPATH\necho CMTROOT is $CMTROOT\n'
command+='echo PATH=$PATH\n'
command+='ulimit -f '+str(fmem)+'\nulimit -v'+str(vmem)+'\nsource '+instDir+'/soffTasks/v0r3/cmt/setup.sh\n'
command+='export ENV_TSQL_URL=mysql://dpnc.unige.ch/nd280calib\n'
command+='bcdataquality.exe -O tpc-bc-root-file='+outfile+' '+filetorun

print command

rtc=os.system(command)
if rtc:
    print rtc;
    sys.exit("failed to run!")

os.system('cd '+base)

print 'Copy output file'

try_command ='lcg-cr -d ' + ND280GRID.DIRSURL(lfn,srm) + '/' + outfile + ' -l ' + lfn + '/' + outfile + ' file:' + outfile
lines,errors=ND280GRID.runLCG(try_command)
if errors:
    sys.exit('Register failed')

print 'Finished OK'

