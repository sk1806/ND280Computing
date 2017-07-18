#!/usr/bin/env python 

#Python script to read and download a list of lfn filenames

import optparse
import os
import sys
import time
import pexpect
import commands
import popen2

# Parser Options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("-o","--outdir",dest="outdir",type="string",help="Output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present")

#Specify -d or -f
parser.add_option("-d","--dir",dest="dir",type="string",help="LFN dir to download")
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to process")

#Optional
parser.add_option("-c","--check",dest="check",type="string",help="To check files in directory, otherwise download (1)")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

outdir=options.outdir
if not outdir:
    sys.exit('Please specify the outdir with -o')

## Check the output directory exists, if not then exit
if not os.path.isdir(outdir):
    sys.exit('The directory ' + outdir + ' does not exist.')

filename=options.filename

check=options.check

dir=options.dir

if not dir and not filename:
    sys.exit('Please specify -d or -f')

counter = 0

filelist=[]

standard='/grid/t2k.org/nd280/'

if dir:
    if standard in dir:
        sys.exit("skip "+standard+" in LFN address")

    command = 'lfc-ls '+standard+dir
    o,i,e=popen2.popen3(command)
    lines=o.readlines()
    for l in lines:
        l.replace('\n','')
        lfn='lfn:'+standard+dir+'/'+l
        filelist.append(lfn)

elif filename:
    print 'Reading file'

    listfile=open(filename,'r')
    filelist=listfile.readlines()

else:
    sys.exit('Please specify -f or -d')

for fl in filelist:
    fl = fl.replace('\n','')
    far=fl.split('/')                
    fname=far[-1]

    print fname

    foutname=outdir + '/' + fname

    print foutname

    if check:
        if os.path.isfile(foutname):
            print 'skipping'
            continue
        else:
            print 'missing, downloading'

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
        time.sleep(1)
    elif trials == 10:
        print 'Failed, skipping'
        continue
    else:
        sys.exit('Failed to download ' + fname)


print 'Downloaded ' + str(counter) + ' files'







