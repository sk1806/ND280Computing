#!/usr/bin/env python

"""
A script that compares the raw files with the processed ones
and outputs one list file with lfn addresses to the processed files
and one for the unprocessed files

G. Wikstrom 2011


Modified to require mandatory run list file since existing functionality
did not permit comparison of input files from one respin against ouput of another
e.g. 5/C numc v.s. 5/E anal
"""

import optparse
import os
import sys
import commands
import ND280GRID

#Parser options

parser = optparse.OptionParser()

#Mandatory (should be positional args!)
parser.add_option("-e","--evtype",dest="evtype",default="spill",  help="Event type: spill (default) or cosmic")
parser.add_option("-l","--level", dest="level", type="string",  help="Processing level: e.g. anal")
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to compare with")

#Mandatory specify -v or -p and -t
parser.add_option("-p","--prod",   dest="prod",   type="string",help="Production, e.g. 4A")
parser.add_option("-v","--version",dest="version",type="string",help="Software version")

#Specifiers
parser.add_option("-i","--input",dest="input",type="string",help="input level")

#Optional
parser.add_option("-u","--exclude", dest="exclude", type="string",help="LFN input file with runs to exclude")
parser.add_option("-o","--output",  dest="output",  type="string",help="Output filename format (for processed, unprocessed, multiple etc", default="")
parser.add_option('--prodir', default='', help='explicitly state path to production output (useful for custom jobs)')

parser.add_option("--verify", help="You must set this to 1 if you're comparing verification files (default=0)", default=0)
(options,args) = parser.parse_args()

###############################################################################

# Main Program
version = options.version
prod    = options.prod
exfile  = options.exclude
level   = options.level
input   = options.input
evtype  = options.evtype
filename= options.filename
verify  = options.verify
prodir  = options.prodir

if (not prod or not filename) or ((not level and not prodir) or (evtype!="spill" and evtype!="cosmic")) or (verify and not version):
    parser.print_help()
    sys.exit(1)


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

#if input == 'raw':
#    input=''


fstart ='_' + evtype + '_'
funtag ='westgrid'
funtag2='triumf'


vname  =prod
basedir='/grid/t2k.org/nd280/'
indir  =''
mcdir  =''

#List raw and processed files in this dataset
#-----------------------------
rawlist=[]
if filename:
    print 'Reading file list from', filename
    listfile=open(filename,'r')
    rawlist=listfile.readlines()
    listfile.close()

    ## make sure these are LFNs
    if len(rawlist):
        if not 'lfn:/' in rawlist[0]:
            print 'Files in '+filename+' are not LFNs!'
            sys.exit(1)
    else:
        'No files in '+filename+'!'
        sys.exit(1)

    ## determine parameters from file list, overrides inputs
    name = ND280GRID.rmNL(rawlist[0]).replace('//','/')
    respinf  = name.split('/')[5]    
    
    if '/verify/' in name:
        version  = name.split('/')[8]
        mctype   = name.split('/')[9]
        run      = name.split('/')[10]
        det      = name.split('/')[11]
        categ    = name.split('/')[12]
        stage    = name.split('/')[13]
        bigrun   = name.split('/')[-1].split('-')[0].split('_')[-1][:4]
        
        mcdir  = basedir+prodnr+'/'+respinf+'/mcp/verify/'+version+'/'+mctype+'/'+run+'/'+det+'/'+categ+'/'+stage+'/'
    else:
        mctype   = name.split('/')[7]
        run      = name.split('/')[8]
        det      = name.split('/')[9]
        categ    = name.split('/')[10]
        stage    = name.split('/')[11]
        bigrun   = name.split('/')[-1].split('-')[0].split('_')[-1][:4]

        mcdir  = basedir+prodnr+'/'+respinf+'/mcp/'+mctype+'/'+run+'/'+det+'/'+categ+'/'+stage+'/'

    # create production output directory path
    if not prodir:
        if verify:
            prodir = basedir+prodnr+'/'+respin +'/mcp/verify/'+version+'/'+mctype+'/'+run+'/'+det+'/'+categ+'/' 
        else:
            prodir = basedir+prodnr+'/'+respin +'/mcp/'+mctype+'/'+run+'/'+det+'/'+categ+'/' 
        prodir+=level


print '-------------------------------------'
print 'Comparing contents of lfn directories:'
print mcdir
print 'and'
print prodir

print 'Running lfc-ls on processed files ...'
outpro = commands.getstatusoutput('lfc-ls ' + prodir)
if outpro[0] != 0:
    sys.exit('Error: ' + str(outpro[0]) + ' no processed files')

#Split the file names into substrings
prolist_all = outpro[1].split()

#Exclude runs from raw file list
extags = []
if exfile:
    print 'Excluding runs from file'

    exlistfile=open(exfile,'r')
    exfilelist=exlistfile.readlines()
    nex=0
    for l in exfilelist:
        l = l.replace('\n','')
        far=l.split('/')                
        rawname=far[-1]
        where=rawname.find(bigrun)
        tag=rawname[where:where+13]
        tag=tag.replace('_','-')
        extags.append(tag)

print 'Comparing ...'

#Fill lists of file numbers and hashcodes
rawnum = []
pronum = []
rawfilelist = []
rawcount = 0
procount = 0
for rawfile in rawlist:
    rawparsed = rawfile.split('_')
    tag=''
    rawparsed = rawfile.split('/')
    rawfile2=rawparsed[-1]
    where=rawfile2.find(bigrun)
#        tset=rawfile2[where+4]
#        if tset != set:
#            continue
    tag=rawfile2[where:where+13]
    tag=tag.replace('_','-')
    
    skip=0
    for extag in extags:
        if tag in extag:
            skip=1
    if skip==1:
        continue
    rawnum.append(tag)
    if filename:
        rawfilelist.append(rawfile.replace('\n',''))
    rawcount += 1

prolist=prolist_all[:]

#Remove those with wrong tags
# For MC there is nothing to remove, but I keep the structre as an example
#for profile in prolist_all:
#    if (fstart not in profile) or (funtag in profile) or (funtag2 in profile):
#        prolist.remove(profile)
#
#Processed tags
for profile in prolist:
    far=profile.split('/')                
    pname=far[-1]
    where=pname.find(bigrun)
    tag=pname[where:where+13]
    pronum.append(tag)
    procount += 1
    
#See which raw files have been processed
processed           = []
unprocessed         = []
processed_level_lfn = []
multiple_level_lfn  = []
unprocessed_lfn     = []

index = 0
for num in rawnum:
    ok = 0
    pindex = 0
    pindex_save = 0
    for pnum in pronum:
        if num == pnum:
            ok += 1
            if ok > 1:
                multiple_level_lfn.append('lfn:' + prodir + '/' + prolist[pindex])
            pindex_save = pindex
        
        pindex += 1

    if ok == 0:
        unprocessed_lfn.append(rawfilelist[index])
    elif ok == 1:
        processed_level_lfn.append('lfn:' + prodir + '/' + prolist[pindex_save])
        
    index += 1


#Write output files containing the processed and unprocessed files
if input:
    evtype=input

processed_level_out_filename  = ''
multiple_level_out_filename   = ''
unprocessed_out_filename      = ''

if options.output:
    processed_level_out_filename  = options.output+'.processed'
    multiple_level_out_filename   = options.output+'.multiple'
    unprocessed_out_filename      = options.output+'.unprocessed'
else:
    processed_level_out_filename  = 'processed_'  +evtype+'_'+vname+'_'+level+'.list'
    multiple_level_out_filename   = 'multiple_'   +evtype+'_'+vname+'_'+level+'.list'
    unprocessed_out_filename      = 'unprocessed_'+evtype+'_'+vname+'_'+level+'.list'
    
rmprocessed_level    = commands.getstatusoutput('rm -rf ' + processed_level_out_filename)
rmmultiple_level     = commands.getstatusoutput('rm -rf ' + multiple_level_out_filename)
rmunprocessed        = commands.getstatusoutput('rm -rf ' + unprocessed_out_filename)
processed_level_out  = open(processed_level_out_filename,'w')
multiple_level_out   = open(multiple_level_out_filename,'w')
unprocessed_out      = open(unprocessed_out_filename,'w')

pindex = 0
for file in processed_level_lfn:
    processed_level_out.write(processed_level_lfn[pindex]+'\n')
    pindex += 1

mindex = 0
for file in multiple_level_lfn:
    multiple_level_out.write(multiple_level_lfn[mindex]+'\n')
    mindex += 1

uindex = 0
for file in unprocessed_lfn:
    unprocessed_out.write(unprocessed_lfn[uindex]+'\n')
    uindex += 1

print 'Wrote: ' + str(pindex) + ' files to ' + processed_level_out_filename
print 'Wrote: ' + str(mindex) + ' files to ' + multiple_level_out_filename
print 'Wrote: ' + str(uindex) + ' files to ' + unprocessed_out_filename
print '---------- Done -----------'

######################################################################
