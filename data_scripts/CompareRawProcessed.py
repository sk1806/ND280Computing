#!/usr/bin/env python

"""
A script that compares the raw files with the processed ones
and outputs one list file with lfn addresses to the processed files
and one for the unprocessed files

G. Wikstrom 2011
"""

import optparse
import os
import sys
import commands

#Parser options

parser = optparse.OptionParser()

#Mandatory (should be positional args!)
parser.add_option("-e","--evtype",dest="evtype",default="spill", help="Event type: spill (default) or cosmic")
parser.add_option("-l","--level", dest="level", type="string",   help="Processing level: e.g. anal")
parser.add_option("-s","--set",   dest="set",   type="string",   help="Set of raw data: e.g. 1,2 for 00001000_00001999,00002000_00002999")

#Specify -v or -p
parser.add_option("-p","--prod",   dest="prod",   type="string",help="Production, e.g. 4A")
parser.add_option("-v","--version",dest="version",type="string",help="Software version")

#Specifiers
parser.add_option("-i","--input",dest="input",type="string",help="input level")

#Optional
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to compare with")
parser.add_option("-u","--exclude", dest="exclude", type="string",help="LFN input file with runs to exclude")
parser.add_option(     "--isCalib", type=int, default=0,          help="Use to implement official calibration directory lookup")
parser.add_option("-o","--output",  dest="output",  type="string",help="Output filename format (for processed, unprocessed, multiple etc", default="")
parser.add_option(     '--prodir',  default='',                   help='explicitly state path to production output (useful for custom jobs)')


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
sets    = options.set
filename= options.filename
verify  = options.verify
prodir  = options.prodir

if (not version and not prod) or not level or (evtype!="spill" and evtype!="cosmic") or not sets or (verify and not version):
    parser.print_help()
    sys.exit(1)
    
respin=''
prodnr=''
if prod:
    respin=prod[-1]
    nr=prod[:-1]
    prodnr='production%03d' % (int(nr))
    # if len(nr) == 1:
    #     prodnr += '00'
    # if len(nr) == 2:
    #     prodnr += '0'
    # prodnr += nr

if input == 'raw':
    input=''


fstart='_' + evtype + '_'
funtag='westgrid'
funtag2='triumf'


for set in sets.split(','):
    
    # dataset = '0000' + set + '000_0000' + set + '999'
    dataset = '%05d000_%05d999' % (int(set),int(set))

    vname=''
    basedir='/grid/t2k.org/nd280/'
    rawdir=basedir + 'raw/ND280/ND280/' + dataset
    if input:
        if version:
            rawdir=basedir+version+'/'+input+'/ND280/ND280/'+dataset
        else:
            rawdir=basedir+prodnr+'/'+respin+'/rdp/ND280/'+dataset+'/'+input

    if not prodir:
        prodir=basedir
        if version:
            if verify:
                prodir += prodnr +'/' + respin + '/rdp/verify/' + version +'/' + level
            else:    
                prodir += version + '/' + level + '/ND280/ND280/' + dataset
            vname=version
        else:
            prodir += prodnr + '/' + respin + '/rdp/ND280/' + dataset + '/' + level
            vname=prod
        if options.isCalib:
            prodir = basedir + 'calib' + '/'+ version + '/ND280/ND280/' + dataset + '/' + level
            vname=version

    print '-------------------------------------'
    print 'Comparing contents of lfn directories:'
    print rawdir
    print 'and'
    print prodir

    #List raw and processed files in this dataset
    #-----------------------------
    rawlist=[]
    if filename:
        print 'Reading files from file: %s' % filename
        listfile=open(filename,'r')
        rawlist=listfile.readlines()
    else:
        print 'Running lfc-ls on raw files ...'
        outraw = commands.getstatusoutput('lfc-ls ' + rawdir)
        if outraw[0] != 0:
            sys.exit('Error: ' + str(outraw[0]) + ' no raw files')
        rawlist = outraw[1].split()

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
            # l = l.replace('\n','')
            # far=l.split('/')                
            # rawname=far[-1]
            # where=rawname.find('0000')
            # tag=rawname[where:where+13]
 
            l = l.strip()

            # extract the run-subrun tag from string (cheaper than creating ND280File and using GetRun())
            # by removing the oa_xx_yyy progenitor and extracting the 13 digit aaaaaaaa-bbbb field
            tag = l.replace('_'.join(l.split('_')[:3])+'_','')[:13]
            tag = tag.replace('_','-')

            extags.append(tag)

    print 'Comparing ...'

    #Fill lists of file numbers and hashcodes
    rawnum      = []
    pronum      = []
    rawfilelist = []
    rawcount    = 0
    procount    = 0

    # print 'rawlist:',rawlist

    for rawfile in rawlist:
        rawparsed = rawfile.split('_')
        tag=''

        if input and not filename:
            if fstart not in rawfile or funtag in rawfile or funtag2 in rawfile:
                continue
            tag = rawparsed[-5]

        elif filename:
            rawparsed = rawfile.split('/')
            rawfile2  = rawparsed[-1]

            # where=rawfile2.find('0000')
            # tset=rawfile2[where+4]
            # if tset != set:
            #     continue
            # tag=rawfile2[where:where+13]
             
            rawfile2 = rawfile2.strip()

            # extract the run-subrun tag from string (cheaper than creating ND280File and using GetRun())
            # by removing the subdetector_ progenitor and extracting the 13 digit aaaaaaaa-bbbb field that follows
            if rawfile2.startswith('nd280_'):
                tag = rawfile2.replace('_'.join(rawfile2.split('_')[:1])+'_','')[:13]
            # respins, however, observe standard oa_nt_xxx* naming convention
            else:
                tag = rawfile2.split('_')[3]
            
            # print 'tag',tag

            if not tag.lstrip('0').startswith(set):
                continue
            
            tag = tag.replace('_','-')
        else:
            subrun = rawparsed[2].split('.')
            tag    = rawparsed[1] + '-' + subrun[0]

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
    for profile in prolist_all:
        if (((fstart not in profile) or (funtag in profile) or (funtag2 in profile))
            and ('timeslip' in level and not 'timeslip' in profile)):
            prolist.remove(profile)


    #Processed tags
    for profile in prolist:
        far   = profile.split('/')                
        pname = far[-1]

        # where=pname.find('0000')
        # tag=pname[where:where+13]

        pname = pname.strip()

        # extract the run-subrun tag from string (cheaper than creating ND280File and using GetRun())
        # by removing the oa_xx_yyy progenitor and extracting the 13 digit aaaaaaaa-bbbb field
        tag = pname.replace('_'.join(pname.split('_')[:3])+'_','')[:13]
 
        pronum.append(tag)
        procount += 1

    #See which raw files have been processed
    processed            = []
    unprocessed          = []
    processed_level_lfn  = []
    multiple_level_lfn   = []
    unprocessed_lfn      = []
    

    #print 'rawnum',rawnum
    #print 'extags',extags
    #print 'pronum',pronum


    index = 0
    for num in rawnum:
        ok = 0
        pindex = 0
        pindex_save = 0
        for pnum in pronum:
            if 'timeslip' in level: pnum = pnum.replace('_','-')
            if num == pnum:
                ok += 1
                if ok > 1:
                    multiple_level_lfn.append('lfn:' + prodir + '/' + prolist[pindex])
                pindex_save = pindex

            pindex += 1

        if ok == 0:
            if filename:
                unprocessed_lfn.append(rawfilelist[index])
            else:
                unprocessed_lfn.append('lfn:' + rawdir + '/' + rawlist[index])
        elif ok == 1:
            processed_level_lfn.append('lfn:' + prodir + '/' + prolist[pindex_save])

        index += 1


    #Write output files containing the processed and unprocessed files
    if input:
        evtype=input

    if options.output:
        processed_level_out_filename  = options.output+'.processed'
        multiple_level_out_filename   = options.output+'.multiple'
        unprocessed_out_filename      = options.output+'.unprocessed'
    else:
        processed_level_out_filename = 'processed_'  +evtype+'_'+vname+'_'+level+'_'+dataset+'.list'
        multiple_level_out_filename  = 'multiple_'   +evtype+'_'+vname+'_'+level+'_'+dataset+'.list'
        unprocessed_out_filename     = 'unprocessed_'+evtype+'_'+vname+'_'+level+'_'+dataset+'.list'

    rmprocessed_level = commands.getstatusoutput('rm -rf ' + processed_level_out_filename)
    rmmultiple_level  = commands.getstatusoutput('rm -rf ' + multiple_level_out_filename )
    rmunprocessed     = commands.getstatusoutput('rm -rf ' + unprocessed_out_filename    )

    processed_level_out = open(processed_level_out_filename,'w')
    multiple_level_out  = open(multiple_level_out_filename, 'w')
    unprocessed_out     = open(unprocessed_out_filename,    'w')

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
