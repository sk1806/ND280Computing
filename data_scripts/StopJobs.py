#!/usr/bin/env python 

import optparse
from ND280GRID import ND280JID
import os
import sys
from subprocess import Popen, PIPE
import smtplib
import commands
import time
import pexpect

from email.MIMEText import MIMEText

#Parser options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("-e","--evtype",dest="evtype",type="string",help="Event type, spill or cosmic", default="spill")
parser.add_option("-o","--outdir",dest="outdir",type="string",help="Output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present")
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to install")

#Specifiers
parser.add_option("-j","--job",dest="job",type="string",help="Job type, Raw, Custom, MC")
parser.add_option("-p","--prod",dest="prod",type="string",help="Production, e.g. 4A")

#Optional
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to process")
parser.add_option("-r","--runno",dest="runno",type="string",help="Run number, or start of - used for listing")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

outdir=options.outdir
if not outdir:
    sys.exit('Please specify -o')

## Check the output directory exsits, if not then exit
if not os.path.isdir(outdir):
    sys.exit('The directory ' + outdir + ' does not exist.')

version = options.version
prod = options.prod
if not version:
    sys.exit('Please specify software version (e.g. v8r5p9) with -v')

evtype=options.evtype
if not evtype:
    sys.exit('Please specify event type with -e')

job=options.job
if not job:
    job='Raw'

runno = options.runno

basename=''
if job == 'Raw' or job == 'MC':
    basename = 'ND280' + job + '_' + evtype
elif job == 'Custom':
    basename = 'ND280' + job

filename=options.filename


counter = 0

if filename:

    print 'Cancelling from file'

    command = 'ls ' + outdir + '/' + basename + '_' + version 
    command += '_0000'
    if runno:
        command += runno
    command += '*.jid'
    print command

    p      = Popen([command],shell=True,stdout=PIPE,stderr=PIPE)
    lines  = p.stdout.readlines()
    errors = p.stderr.readlines()

    djids = lines

    listfile=open(filename,'r')
    filelist=listfile.readlines()

    for l in filelist:
        l = l.replace('\n','')
        far=l.split('/')                
        rawname=far[-1]
        if runno:
            rtag='_0000'+runno
            if not rtag in rawname:
                continue

        where=rawname.find('0000')
        tag=rawname[where:where+13]
        tag=tag.replace('-','_')
        rname=basename + '_' + version + '_' + tag

        lname=outdir + '/'
        indir=0
        for d in djids:
            if rname in d:
                d=d.replace('\n','')
                dar=d.split('/') 
                indir=1
                lname+=dar[-1]
                break

        if indir == 0 or not os.path.isfile(lname):
            print 'File not there: ' + lname
            continue

        print lname
        
        fjid = open(lname,"r")
        flines = fjid.readlines()
        joblink = flines[1] 
        print joblink
        
        command = 'glite-wms-job-cancel ' + joblink
        
        child = pexpect.spawn(command,timeout=30)
        ii=child.expect(['.* : ','.*:'])
        if ii == 1:
            child.sendline('q')
            print 'No job'
            continue
        child.sendline('y')
        
        ii=child.expect(['Error',pexpect.TIMEOUT,pexpect.EOF])
        
        if ii == 2:
            counter += 1
            print child.before
            time.sleep(0.1)
        elif ii < 1:
            print child.after

else:
    print 'Cancelling from ls'

    command = 'ls ' + outdir + '/' + basename + '_' + version
    if runno:
        command += '_0000' + runno + '*.jid'
    else:
        command += '_*.jid'

    p      = Popen([command],shell=True,stdout=PIPE,stderr=PIPE)
    lines  = p.stdout.readlines()
    errors = p.stderr.readlines()

    print command    
        
    for l in lines:
        l = l.replace('\n','')
        print l
        fjid = open(l,"r")
        flines = fjid.readlines()
        joblink = flines[1] 
        print joblink
        
        command = 'glite-wms-job-cancel ' + joblink
        
        child = pexpect.spawn(command,timeout=30)
        ii=child.expect(['.* : ','.*:'])
        if ii == 1:
            child.sendline('q')
            print 'No job'
            continue
        child.sendline('y')
        
        ii=child.expect(['Error',pexpect.TIMEOUT,pexpect.EOF])
        
        if ii == 2:
            counter += 1
            print child.before
            time.sleep(0.1)
        elif ii < 1:
            print child.after

print 'Cancelled ' + str(counter) + ' jobs'







