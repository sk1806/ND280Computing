#!/usr/bin/env python 

#Python script to download the latest EGI certificates and install them in the correct directory
#They should be installed in $X509_CERT_DIR

import optparse
import os
import sys
import time
import pexpect
import commands
import popen2

# Parser Options
parser = optparse.OptionParser()
parser.add_option("-i","--instdir",dest="instdir",type="string",help="Installation directory path")
parser.add_option("-t","--tempdir",dest="tempdir",type="string",help="Temporary directory path")
parser.add_option("-m","--mode",dest="mode",type="string",help="Operation mode")

###############################################################################

# Main Program

instdir=options.instdir
tempdir=options.tempdir
case=int(options.mode)
if not instdir or not tempdir or not mode:
    sys.exit('Please specify -i -t and -m')

#Modes
#0 = get list
#1 = wget
#2 = unpack
#3 = copy to dir

path='repository.egi.eu/sw/production/cas/1/current/'

#Download list
if case == 0:
    command = 'wget ' + path + 'ca-policy-egi-core.list '+tempdir
    o,i,e=popen2.popen3(command)
    sys.exit('Downloaded list')

#Get files in list
listfile=open('ca-policy-egi-core.list','r')
filelist=listfile.readlines()
counter=0
for fl in filelist:

    if '#' in fl:
        continue
    fl = fl.replace('-1\n','')
    print fl

    if nor 'ca_' in flname:
        continue

    flname = fl + '.tar.gz'

    #Download files
    if case == 1:
        fullpath = path + 'tgz/' + flname
        print fullpath
        command = 'wget ' + fullpath + ' ' + tempdir

    #Unzip files
    if case == 2:
        command = 'cd '+tempdir+'\n'
        command += 'gunzip ' + flname+ ';tar -xvf '+flname.replace('.gz','')+'\n'
        command += 'cd -'

    #Copy files to new directory
    if case == 3:
        flname=flname.replace('.tar.gz','')
        command = 'cp '+tempdir+'/'+flname+'/* '+instdir

    print command
    o,i,e=popen2.popen3(command)
    files=o.readlines()
    err=e.readlines()
    if not err:
        print 'OK'
        counter += 1
    else:
        for el in err:
            print el

print 'Downloaded ' + str(counter) + ' files'







