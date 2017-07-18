#!/usr/bin/env python

"""
A script that produces a list file with lfn addresses

G. Wikstrom 2011
"""

import optparse
import os
import sys
import commands

#Parser options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("-s","--set",dest="set",type="string",help="Set of data, e.g. 1 for 00001000_00001999")

#Specify -v or -p and -t
parser.add_option("-p","--prod",dest="prod",type="string",help="Production, e.g. 4A")
parser.add_option("-t","--type",dest="type",type="string",help="Production type, mcp or rdp")
parser.add_option("-v","--version",dest="version",type="string",help="Software version")

#Optional
parser.add_option("-d","--dir",dest="dir",type="string",help="LFN input directory path")
parser.add_option("-e","--evtype",dest="evtype",type="string",help="Event type, spill (default) or cosmic", default="spill")
parser.add_option("-l","--level",dest="level",type="string",help="Processing level, e.g. raw or reco")
parser.add_option("-o","--outdir",dest="outdir",type="string",help="Output directory path")
parser.add_option("-u","--exclude",dest="exclude",type="string",help="LFN input file with runs to exclude")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

version = options.version
prod = options.prod
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

dir=options.dir
exfile=options.exclude
dtype = options.type
if not dtype:
    dtype = 'rdp'
set = options.set
if not set:
    sys.exit('Please specify dataset (e.g. 1) with -s')

dataset = '0000' + set + '000_0000' + set + '999'

evtype=options.evtype
funtag='westgrid'
funtag2='triumf'

level = options.level
if not level:
    level = 'raw'

if level != 'raw' and not version and not prod:
    sys.exit('Please specify software version (e.g. v8r5p9) with -v or production (e.g. 4A) with -p')    

outdir=options.outdir
if not outdir:
    outdir=os.getenv("ND280JOBS")
    outdir+='/lists'

if not os.path.isdir(outdir):
    out = commands.getstatusoutput('mkdir ' + outdir)

#Directory to check
checkdir='/grid/t2k.org/nd280/'
if version:
    checkdir += version + '/' + level + '/ND280/ND280/' + dataset
elif prod:
    checkdir += prodnr + '/' + respin + '/' + dtype + '/ND280/' + dataset + '/' + level
else:
    checkdir += level + '/ND280/ND280/' + dataset

#If user has specified directory
if dir:
    checkdir = '/grid/t2k.org/nd280/' + dir

print '-------------------------------------'
print 'Looking at lfn directory:'
print checkdir

#List the files in this dataset
print 'Accessing the grid ...'

outcheck = commands.getstatusoutput('lfc-ls ' + checkdir)
if outcheck[0] != 0:
    sys.exit('Error: ' + str(outcheck[0]) + ' no files in directory')

#Split the file names in to substrings
checklist = outcheck[1].split()

if evtype:
    checklist_mod=checklist[:]
    for checkfile in checklist:
        if (evtype not in checkfile) or (funtag in checkfile) or (funtag2 in checkfile):
            checklist_mod.remove(checkfile)
    checklist=checklist_mod

#Write output files containing the processed and unprocessed files
checkfiles_out_filename = level+'_'+dataset+'.list'

#For a specified directory
if dir:
    dira=dir.split('/')
    dirname=''
    for dpart in dira:
        dirname+=dpart+'_'
    dirname+='.list'
    checkfiles_out_filename=dirname.replace('_.list','.list')

checkfiles_out = open(checkfiles_out_filename,'w')

if exfile:
    print 'Excluding runs from file'

    exlistfile=open(exfile,'r')
    exfilelist=exlistfile.readlines()
    nex=0
    for l in exfilelist:
        l = l.replace('\n','')
        far=l.split('/')                
        rawname=far[-1]
        where=rawname.find('0000')
        tag=rawname[where+4:where+13]
        tag=tag.replace('_','-')
        for checkfile in checklist:
            if tag in checkfile:
                checklist.remove(checkfile)
                nex+=1
                break
        
    print 'Excluding '+str(nex)+' runs'

checkcount = 0
for checkfile in checklist:
    checkfiles_out.write('lfn:' + checkdir + '/' + checkfile +'\n')
    checkcount += 1

out = commands.getstatusoutput('mv -f ' + checkfiles_out_filename + ' ' + outdir)

print 'Wrote '+str(checkcount)+' runs to list file:'
print ' ' + checkfiles_out_filename
print ' in '
print ' ' + outdir
print '---------- Done -----------'

######################################################################
