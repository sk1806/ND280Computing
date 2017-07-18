#!/usr/bin/env python

"""
A script that removes processed files from a LFC (logical file catalog)

G. Wikstrom 2011
"""

import optparse
import os
import sys
import commands
import time

#Parser options
parser = optparse.OptionParser()

#Mandatory (should be positional arguments!)
parser.add_option("-e","--evtype", dest="evtype", type="string",help="Event type: i.e. spill or cosmic", default="spill")
parser.add_option("-l","--level",  dest="level",  type="string",help="Processing level: e.g. anal or all")
parser.add_option("-s","--set" ,   dest="set",    type="string",help="Set of raw data: e.g. 1 for 00001000_00001999")

#Specify either -v or -p and -t
parser.add_option("-p","--prod",   dest="prod",   type="string",help="Production: e.g. 4A")
parser.add_option("-t","--type",   dest="type",   type="string",help="Production type: mcp or rdp, add verify for verification, e.g. rdpverify")
parser.add_option("-v","--version",dest="version",type="string",help="Software version: e.g. v9r11p9")

#Optional
parser.add_option("-c","--clean",   dest="clean",   type="string",help="Clean the files (tag specific) not in file")
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to process")
parser.add_option("-r","--runno",   dest="runno",   type="string",help="Run number and 4-character tag, as 3517-0000_jyyt")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

version = options.version
prod    = options.prod
dtype   = options.type
level   = options.level
evtype  = options.evtype
set     = options.set
filename= options.filename
runno   = options.runno
clean   = options.clean

if dtype != 'mcp':
    if not filename and not level:
        if (not version and not prod) or (prod and not dtype) or (version and not dtype) or not level or (evtype!="spill" and evtype!="cosmic") or not set:
            parser.print_help()
            sys.exit(1)
else:
    if not filename and not level:
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

verify = ''
if len(dtype) > 3:
    verify = dtype[3:]
    dtype = dtype[:3]

if evtype == 'spill' or evtype == 'spl':
    fstart='oa_nd_spl'
elif evtype == 'cosmic' or evtype == 'cos':
    fstart == 'oa_nd_cos'
else:
    fstart = ''

# tags to test later
funtag  ='westgrid'
funtag2 ='triumf'


if set:
    # dataset = '0000' + set + '000_0000' + set + '999'
    dataset = '%05d000_%05d999' % (int(set),int(set))
else:
    dataset = ''

levels = []

if dtype == 'rdp':
    if not level:
        levels = ['anal','cali','cata','cnfg','logf','reco','unpk']
    
elif dtype == 'mcp':
    # for mcp derive production directory exclusively from input file list
    print 'Reading files from file %s ' % (filename)
    if not os.path.exists(filename): sys.exit('Input file: %s not found!'%filename)
    listfile=open(filename,'r')
    rawlist=listfile.readlines()
    listfile.close()

    ## determine parameters from first file in list, overrides inputs
    if not rawlist: sys.exit('no multiples!')
    name     = rawlist[0].strip().replace('//','/')
    basedir  = '/'+('/').join(name.split('/')[1:4])+'/'
    prodnr   = name.split('/')[4]
    respinf  = name.split('/')[5]    
    bigrun   = name.split('/')[-1].split('-')[0].split('_')[-1][:4]    

    if not verify:
        mctype = name.split('/')[7]
        run    = name.split('/')[8]
        det    = name.split('/')[9]
        categ  = name.split('/')[10]
        mcdir  = basedir+prodnr+'/'+respinf+'/mcp/'+mctype+'/'+run+'/'+det+'/'+categ
    else:
        version = name.split('/')[8]
        mctype  = name.split('/')[9]
        run     = name.split('/')[10]
        det     = name.split('/')[11]
        categ   = name.split('/')[12]
        mcdir   = basedir+prodnr+'/'+respinf+'/mcp/verify/'+version+'/'+mctype+'/'+run+'/'+det+'/'+categ

if level != 'all' and level not in levels:
    levels.append(level)
    fstart = ''

count = 0        

#Loop over the processing levels
for this_level in levels:
    
    if (level != 'all') and (this_level != level):
        continue

    if dtype!= 'mcp':
        prodir='/grid/t2k.org/nd280/'

        if prod:
            if verify:
                prodir += prodnr + '/' + respin + '/' + dtype + '/' + verify + '/' + version + '/' + this_level
            else:
                prodir += prodnr + '/' + respin + '/' + dtype + '/ND280/' + dataset + '/' + this_level
        else:
            prodir += version + '/' + this_level + '/ND280/ND280/' + dataset
    else:
        prodir = mcdir + '/' + level
    
    if prodir.endswith('/'): 
        prodir = prodir.rstrip('/')
            
    print '----------------------------------------'
    print 'Deleting files in ' + prodir

    outpro = commands.getstatusoutput('lfc-ls ' + prodir)
    if outpro[0] != 0:
        print 'No files to delete'
        continue
        
    prolist_all = outpro[1].split()
    prolist = prolist_all[:]

    #Remove those with wrong tags
    for profile in prolist_all:
        if (fstart not in profile) or (funtag in profile) or (funtag2 in profile):
            prolist.remove(profile)

    #Read a list of lfn files
    #---------------------------------------
    if filename:

        if not os.path.exists(filename): sys.exit('Input file: %s not found!'%filename)
        listfile=open(filename,'r')
        filelist=listfile.readlines()
        listfile.close()

        if len(filelist) == 0:
            sys.exit('No lines in input file!')

        #To clear out files not in file
        if clean:
            for profile in prolist:
                print profile
                rm = 1
                for f in filelist:
                    fname=f.replace('\n','')
                    far=fname.split('/')                
                    name=far[-1]
                    rname = name[14:28]
                    if len(rname) == 0:
                        rm = 0
                        break
                    if rname in profile:
                        rm = 0

                if rm == 1:
                    if prodir.endswith('/'): 
                        prodir = prodir.rstrip('/')
                    propath = 'lfn:' + prodir + '/' + profile
                    print 'Deleting file ' + propath
                    
                    outdel = commands.getstatusoutput('lcg-del -a ' + propath)
                    if outdel[0] != 0:
                        print 'Error: ' + str(outdel[0]) + ' delete failed'
                        outlg = commands.getstatusoutput('lcg-lg ' + propath)
                        outlr = commands.getstatusoutput('lcg-lr ' + propath)
                        outuf = commands.getstatusoutput('lcg-uf -v ' + outlg[1] + ' ' + outlr[1])
                        print outuf[1]
                        
                    count += 1
                    time.sleep(1)
                
        else:
            for f in filelist:
                fname=f.replace('\n','')
                far=fname.split('/')                
                rawname=far[-1]
                rname = ''

                if runno:
                    rname=rawname[14:28]
                    if len(rname) == 0:
                        continue
                else:
                    if 'nd280_' in rawname:
                        rname=rawname.replace('nd280_','')
                        rname=rname.replace('_','-')
                        rname=rname.replace('.daq.mid.gz','')
                    else:
                        rname = rawname

                print 'rname ' + rname

                matchfile=''
                for profile in prolist:
                    if rname in profile:
                        matchfile=profile
                        break
                if matchfile == '':
                    print 'File not on lfn'
                    continue

                print matchfile

                if prodir.endswith('/'): 
                    prodir = prodir.rstrip('/')
                propath = 'lfn:' + prodir + '/' + matchfile
                print 'Deleting file ' + propath

                outdel = commands.getstatusoutput('lcg-del -a ' + propath)
                if outdel[0] != 0:
                    print 'Error: ' + str(outdel[0]) + ' delete failed'
                    outlg = commands.getstatusoutput('lcg-lg ' + propath)
                    outlr = commands.getstatusoutput('lcg-lr ' + propath)
                    outuf = commands.getstatusoutput('lcg-uf -v ' + outlg[1] + ' ' + outlr[1])
                    print outuf[1]
                
                count += 1
                time.sleep(1)


    #Remove a certain run number
    #---------------------------------------
    elif runno:
        
        matchfile=''
        for profile in prolist:
            if runno in profile:
                matchfile=profile
                break
        if matchfile == '':
            print 'File not on lfn'
            continue
                
        if prodir.endswith('/'): 
            prodir = prodir.rstrip('/')
        propath = 'lfn:' + prodir + '/' + matchfile
        print 'Deleting file ' + propath
        
        outdel = commands.getstatusoutput('lcg-del -a ' + propath)
        if outdel[0] != 0:
            print 'Error: ' + str(outdel[0]) + ' delete failed'
            outlg = commands.getstatusoutput('lcg-lg ' + propath)
            outlr = commands.getstatusoutput('lcg-lr ' + propath)
            outuf = commands.getstatusoutput('lcg-uf -v ' + outlg[1] + ' ' + outlr[1])
            print outuf[1]
        
        count += 1
        time.sleep(1)


    #Remove all files in a directory
    #---------------------------------------
    else:
    
        for profile in prolist:
            print 'Deleting ' + profile
            
            if prodir.endswith('/'): 
                prodir = prodir.rstrip('/')
            propath = 'lfn:' + prodir + '/' + profile
            
            outdel = commands.getstatusoutput('lcg-del -a ' + propath)
            if outdel[0] != 0:
                print 'Error: ' + str(outdel[0]) + ' delete failed'
                outlg = commands.getstatusoutput('lcg-lg ' + propath)
                outlr = commands.getstatusoutput('lcg-lr ' + propath)
                outuf = commands.getstatusoutput('lcg-uf -v ' + outlg[1] + ' ' + outlr[1])
                print outuf[1]
            
            count += 1
            time.sleep(1)

   


print 'Deleted ' + str(count) + ' files'
print '-------------------Done-------------------------'
