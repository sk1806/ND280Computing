#!/usr/bin/env python 

import optparse
from ND280GRID import ND280JID, runLCG
import os
import sys
import commands
import time
import pexpect

#Parser Options
parser = optparse.OptionParser()

#Mandatory (should be args not options!)
parser.add_option("-e","--evtype",  type="string",help="[mandatory] Event type, spill or cosmic", default="spill")
parser.add_option("-o","--outdir",  type="string",help="[mandatory] Output directory path")
parser.add_option("-v","--version", type="string",help="[mandatory] Version of nd280 software to install")
parser.add_option("-p","--prod",    type="string",help="[mandatory] Production, e.g. 4A")

#Optional
parser.add_option("-j","--job",               default='Raw',help="Job type, Raw, Custom, MC")
parser.add_option("-f","--filename",          default='',   help="File containing filenames to process")
parser.add_option("-r","--runno",             default='',   help="Run number, or start of - used for listing")
parser.add_option(     "--nBatch",  type=int, default=250,  help="Number of statuses to simultaneously check")
(options,args) = parser.parse_args()

##############################################################################

# Main Program
version  = options.version
prod     = options.prod
job      = options.job
evtype   = options.evtype
filename = options.filename
runno    = options.runno
outdir   = options.outdir

if not version or (evtype!="spill" and evtype!="cosmic") or not outdir:
    parser.print_help()
    sys.exit(1)

basename=''
if job == 'Raw' or job == 'MC':
    basename = 'ND280' + job + '_' + evtype
elif job == 'Custom':
    basename = 'ND280' + job

set=''
if runno:
    set = runno[0]


## Check the output directory exsits, if not then exit
if not os.path.isdir(outdir):
    sys.exit('The directory ' + outdir + ' does not exist.')

lfnbase = 'lfn:/grid/t2k.org/nd280/raw/ND280/ND280/'

nameend=''
vflag=version
if prod:
    vflag = prod
if set and not runno:
    vflag += '_' + set
if runno:
    nameend=vflag + '_' + job + '_' + evtype + '_' + runno + '.list'
else:
    nameend=vflag + '_' + job + '_' + evtype + '.list'

#Write file with running runs
running_filename  = 'running_status_' + nameend
rmrunning         = commands.getstatusoutput('rm -rf ' + running_filename)
running_out       = open(running_filename,'w')

#Write file with waiting runs
waiting_filename  = 'waiting_status_' + nameend
rmwaiting         = commands.getstatusoutput('rm -rf ' + waiting_filename)
waiting_out       = open(waiting_filename,'w')

#Write file with unclear runs
unclear_filename  = 'unclear_status_' + nameend
rmunclear         = commands.getstatusoutput('rm -rf ' + unclear_filename)
unclear_out       = open(unclear_filename,'w')

#Write file with cleared runs
clear_filename    = 'cleared_status_' + nameend
rmclear           = commands.getstatusoutput('rm -rf ' + clear_filename)
clear_out         = open(clear_filename,'w')

#Write file with failed runs
failed_filename   = 'failed_status_' + nameend
rmfailed          = commands.getstatusoutput('rm -rf ' + failed_filename)
failed_out        = open(failed_filename,'w')

#Write file with failed runs
failedce_filename = 'failed_ce_info_' + nameend
rmfailedce        = commands.getstatusoutput('rm -rf ' + failedce_filename)
failedce_out      = open(failedce_filename,'w')

#Write file with OK runs
OK_filename       = 'ok_status_' + nameend
rmok              = commands.getstatusoutput('rm -rf ' + OK_filename)
OK_out            = open(OK_filename,'w')

#Write file with missing runs
missing_filename  = 'missing_status_' + nameend
rmmissing         = commands.getstatusoutput('rm -rf ' + missing_filename)
missing_out       = open(missing_filename,'w')

#File of jids to be checked
tmpjid            = outdir + '/tmpjid.txt'



ninput  =0
nmissing=0
jids    =[]
#Input file
#-----------------------------
if filename:
    print 'Status from file'

    command = 'ls ' + outdir + '/' + basename + '_' + version 
    command += '_0000'
    if runno:
        command += runno
    command += '*.jid'
    print command
    lines,errors = runLCG(command,is_pexpect=False)
    djids        = lines

    listfile=open(filename,'r')
    filelist=listfile.readlines()

    for l in filelist:
        ninput+=1
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

        if indir == 1 and os.path.isfile(lname):
            jids.append(lname)
        else:
            nmissing+=1
            missing_out.write(l+'\n')
            print 'File not there: ' + lname
            continue

    # print jids

#Loop over jids
#-----------------------------
else:
    print 'Loop over jid files...'
    command = 'ls ' + outdir + '/' + basename + '_' + version 
    #command += '_0000'
    if runno:
        command += runno
    command += '*.jid'
    print command
    lines,errors = runLCG(command,is_pexpect=False)
    jids         = lines
    jiderrors    = errors

#----------------------------------------------
allcounter = 0
unclear    = 0
ok         = 0
failed     = 0
running    = 0
waiting    = 0
counter    = 0
clear      = 0

#Call glite-wms-job-status in packets of size nl
nl = options.nBatch
njids=len(jids)
print njids
for i in range(0,njids/nl+1):
    print str(i) + ' ' + str(counter)

    #Write file with jid addresses
    rmtmp = commands.getstatusoutput('rm -rf '+ tmpjid)
    tmpout = open(tmpjid,'w')
    jidlines = {}
    for j,l in enumerate(jids):
        if j < i*nl:
            continue
        if j >= (i+1)*nl:
            break
        lname = l.replace('\n','')
        fout = open(lname,"r")
        flines = fout.readlines()
        for fline in flines:
            if not 'http' in fline:
                continue
            tmpout.write(fline)
            jidlines[str(fline.replace('\n',''))] = str(lname)
            counter += 1

        fout.close()

    tmpout.close()

    #Get status
    #--------------------------------------------
    print 'Getting status'
    command = "glite-wms-job-status --noint -i " + tmpjid
    child = pexpect.spawn(command,timeout=30)
    #child.expect('.*:')
    #child.sendline('a')

    ii = 0
    timeouts = 0
    index = -1
    while ii < 3 and timeouts < 10:
        ii = child.expect(["Success ===========",pexpect.TIMEOUT,pexpect.EOF])
        if ii == 1:
            print 'Timeout!'
            timeouts += 1
            time.sleep(10)
            continue
        if ii == 2:
            break
        
        ii = child.expect(["Error",pexpect.TIMEOUT,"https://[a-zA-Z0-9_:/.-]+",pexpect.EOF])

        if ii == 0:
            print 'glite-wms-job-status error'
            print child.match.groups()[0]
            continue
        if ii == 1:
            print 'Timeout!'
            timeouts += 1
            time.sleep(10)
            continue
        if ii == 3:
            break

        print '-----------------------------------'
        allcounter += 1
        index += 1

        site = str(child.after)
        print 'Site: ', site

        #Get jid name
        if not site in jidlines:
            print 'Site error: '+ site
            continue
        
        jid = jidlines[site]
        jid = jid.replace('\n','')
        jar=jid.split('/')                
        jidname=jar[-1]
        midname=jidname.replace(basename + '_','nd280')
        midname=midname.replace(version,'')
        numtag=midname[6:19]
        midname='nd280_'+numtag+'.daq.mid.gz'

        set = midname[10]
        dataset = '0000' + set + '000_0000' + set + '999'

        rawname=lfnbase + dataset + '/' + midname

        print jid
        print midname

        sar = site.split('/')
        sitelong = sar[-2]
        sitelongar = sitelong.split(':')
        site = sitelongar[0]
        print 'WMS:  ' + site

        ii = child.expect(["Current Status: \s+([a-zA-Z0-9_() ]+)",pexpect.EOF])

        #### Get the current status
        status=''
        exitcode=''
        dest=''
        if ii == 0:
            status = child.match.groups()[0]
        else:
            print 'Info failed'
            unclear_out.write(rawname + '\n')
            unclear += 1
            continue 

        if 'Cancelled' in status:
            print 'Cancelled'
            unclear_out.write(rawname + '\n')
            unclear += 1
            continue 

        elif "Done" in status:
            ii=child.expect(["Exit code: \s+([0-9]+)",pexpect.EOF])
            if ii == 0:
                exitcode = child.match.groups()[0]
            else:
                print 'Unclear 1 ' + str(ii)
                unclear_out.write(rawname + '\n')
                unclear += 1
                continue
        elif "Waiting" in status:
            print status
            waiting_out.write(rawname + '\n')
            waiting += 1
            continue

        ii=child.expect(["Status Reason:  \s+([a-zA-Z0-9_]+)",pexpect.EOF])
        if ii == 0:
            statusreason=child.match.groups()[0]
        else:
            print 'Unclear 2 ' + str(ii)
            unclear_out.write(rawname + '\n')
            unclear += 1
            continue

        if 'Done' in status or 'Running' in status or 'Scheduled' in status:
            ii=child.expect(["Destination:   \s+([a-zA-Z0-9_.]+)",pexpect.EOF])
            if ii == 0:
                dest=child.match.groups()[0]
                print 'CE:   ' + dest
            else:
                print 'Unclear 3 ' + str(ii)
                unclear_out.write(rawname + '\n')
                unclear += 1
                continue

        if 'Done' in status:
            if exitcode == '0' and not 'Failed' in status:
                print 'OK'
                OK_out.write(rawname + '\n')
                ok += 1
            else:
                print 'Failed'
                failed_out.write(rawname + '\n')
                failedce_out.write(dest + ' ' + rawname + '\n')
                failed += 1
        elif 'Aborted' in status or 'Undef' in status or 'Unknown' in status:
            print status
            unclear_out.write(rawname + '\n')
            unclear += 1
        elif 'Running' in status:
            print status
            running_out.write(rawname + '\n')
            running += 1
        elif 'Scheduled' in status or 'Ready' in status or 'Waiting' in status or 'Submitted' in status:
            print status
            waiting_out.write(rawname + '\n')
            waiting += 1
        elif 'Cleared' in status:
            print 'Cleared'
            clear_out.write(rawname + '\n')
            clear += 1
        else:
            print 'Strange value: ' + status


#-------------------------------------------------------------
print 'Checked ' + str(allcounter) + ' jobs'
if filename:
    print str(ninput) + ' input files'
print str(counter) + ' jid files'
print str(running) + ' running jobs written to '   + running_filename
print str(waiting) + ' waiting jobs written to '   + waiting_filename
print str(ok)      + ' OK runs written to '        + OK_filename
print str(failed)  + ' failed runs written to '    + failed_filename
print str(failed)  + ' failed ce info written to ' + failedce_filename
print str(unclear) + ' unclear runs written to '   + unclear_filename
print str(clear)   + ' cleared runs written to '   + clear_filename
if filename:
    print str(nmissing) + ' missing runs written to ' + missing_filename
print 'Checksum ' + str(unclear + failed + ok + running + waiting + clear) + ' ' + str(allcounter)

