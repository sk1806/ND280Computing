#!/usr/bin/env python 

#Python script to download logfiles, tar them and store ball on LFN

import optparse
import os
import sys
import time
import pexpect
import commands
import popen2

from email.MIMEText import MIMEText

# Parser Options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("-e","--evtype",dest="evtype",type="string",help="Event type, spl or cos")
parser.add_option("-s","--set",dest="set",type="string",help="Set of raw data, e.g. 1 for 00001000_00001999")
parser.add_option("-o","--outdir",dest="outdir",type="string",help="Output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present")

#Specify either -v or -p and -t
parser.add_option("-p","--prod",dest="prod",type="string",help="Production, e.g. 4A")
parser.add_option("-t","--type",dest="type",type="string",help="Production type, mcp or rdp, add verify for verification, e.g. rdpverify")
parser.add_option("-v","--version",dest="version",type="string",help="Software version")

#Specify -d or -u
parser.add_option("-u","--upload",dest="upload",type="string",help="Upload tar ball to LFN")
parser.add_option("-d","--download",dest="download",type="string",help="Download LFN files")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

evtype=options.evtype
if evtype == 'spill':
    evtype = 'spl'
if evtype == 'cosmic':
    evtype = 'cos'
if not evtype:
    sys.exit('Please specify event type with -e')

set = options.set
if not set:
    sys.exit('Please specify dataset (e.g. 1) with -s')

dataset = '0000' + set + '000_0000' + set + '999'

outdir=options.outdir
if not outdir:
    sys.exit('Please specify the outdir with -o')

## Check the output directory exists, if not then exit
if not os.path.isdir(outdir):
    sys.exit('The directory ' + outdir + ' does not exist.')

version = options.version
prod = options.prod
if not version and not prod:
    sys.exit('Please specify software version (e.g. v8r5p9) with -v or production (e.g. 4A) with -p')
respin=''
prodnr=''
if prod:
    respin=prod[-1]
    prodnr='production'
    nr=prod[:-1]
    if len(nr) == 1:
        prodnr += '00'
    if len(nr) == 2:
        prodnr += '0'
    prodnr += nr

dtype = options.type
if prod and not dtype:
    sys.exit('Please specify production type with -t')

verify = ''
if len(dtype) > 3:
    verify = dtype[3:]
    dtype = dtype[:3]

if verify and not version:
    sys.exit('Please specify software version with -v')

upload=options.upload
download=options.download

if not download and not upload:
    sys.exit('Please set either -d or -u')

counter = 0

filelist=[]

standard='/grid/t2k.org/nd280/'


lfnpath=standard
path=''
if prod:
    if verify:
        path = prodnr + '/' + respin + '/' + dtype + '/' + verify + '/' + version + '/logf'
    else:
        path = prodnr + '/' + respin + '/' + dtype + '/ND280/' + dataset + '/logf'
else:
    path = version + '/logf/ND280/ND280/' + dataset

lfnpath=standard+path

tarfile='logf_'+str(set)+'.tgz'

if download:

    print 'Checking ' + lfnpath

    filelist=[]
    command = 'lfc-ls '+lfnpath
    o,i,e=popen2.popen3(command)
    lines=o.readlines()
    counter=0
    for l in lines:
        l.replace('\n','')
        if '.log' not in l:
            continue
        counter+=1
        lfn='lfn:'+lfnpath+'/'+l
        filelist.append(lfn)
        if counter == 2:
            break

    print 'Downloading files from ' + lfnpath

    localfiles=[]
    for fl in filelist:
        fl = fl.replace('\n','')
        far=fl.split('/')                
        fname=far[-1]
        localfiles.append(fname)
        
        print fname

        foutname=outdir + '/' + fname

        command = 'lcg-cp ' + fl + ' ' + foutname

        ii=0
        trials=0
        while ii < 3 and trials < 10:
            rmfile = commands.getstatusoutput('rm -rf ' + foutname)
            child = pexpect.spawn(command,timeout=4000)
            ii=child.expect(['Error','error',pexpect.TIMEOUT,'No such file',pexpect.EOF])
            if ii < 3:
                trials += 1
                print 'Retrying...'

        if ii == 4:
            counter += 1
            print child.before
            time.sleep(0.1)
        elif trials == 10:
            print 'Failed, skipping'
            continue
        else:
            sys.exit('Failed to download ' + fname)

    print 'Downloaded ' + str(counter) + ' files'

    print 'Tarring files'

    command='tar -czf '+tarfile
    startdir=os.getcwd()
    os.chdir(outdir)
    for fl in localfiles:
        fl = fl.replace('\n','')
        command+=' '+fl
    os.system(command)
    os.chdir(startdir)

    print 'Tarred '+str(len(localfiles))+' files to '+tarfile

if upload:
    
    print 'Uploading file '+tarfile+' to '+path
    srm='srm://srm-t2k.gridpp.rl.ac.uk/castor/ads.rl.ac.uk/prod/t2k.org/nd280/'
    srm+=path
    command='lcg-cr -d '+srm+'/'+tarfile+' -l '+lfnpath+'/'+tarfile+' file:'+outdir+'/'+tarfile

    os.system(command)

    print 'Done'
