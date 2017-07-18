#!/usr/bin/env python

#---------------------------------------------------------------
#Script to submit nd280 software installation jobs to grid CEs
#Remember to change proxy to Role=lcgadmin
#---------------------------------------------------------------

import optparse
import ND280GRID
import os
import time
import pexpect
import commands
import sys

from siteList import site_list

#Parser Options

parser = optparse.OptionParser()

#Mandatory
parser.add_option("-c","--ce",     dest="ce",      type="string",help="CE to install on, e.g. 0 for lcgce05.gridpp.rl.ac.uk:8443/cream-pbs-grid1000M, a CE number, or all for all CEs [MANDATORY]")
parser.add_option("-v","--version",dest="version", type="string",help="Version of nd280 software to install [MANDATORY]")

#Optional
parser.add_option("-b","--beam",   dest="beam",    type="string",help="Set to 1 to just get beam data")
parser.add_option("-d","--delete", dest="delete",  type="string",help="Set to 1 to delete this version")
parser.add_option("-f","--forced", dest="forced",  type="string",help="Set to 1 to force install")
parser.add_option("-m","--module", dest="module",  type="string",help="To install one specific module inside an existing nd280 package, e.g. ecalRecon,v0r0")
parser.add_option("-n","--name",   dest="name",    type="string",help="To specify a name to installation directory and tag, e.g. v9r7p5mod")
parser.add_option("-o","--outdir", dest="outdir",  type="string",help="Output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present")
parser.add_option("-u","--unmake", dest="unmake",  type="string",help="Set to 1 to run cmt broadcast make clean")
parser.add_option("-x","--compile",dest="compile", type="string",help="Set to 1 to just compile this module")
(options,args) = parser.parse_args()

###############################################################################

# Main Program

nd280ver = options.version
ce=options.ce

if not nd280ver or not ce:
    parser.print_help()
    print '\nSitesList:'
    for index,site in enumerate(site_list):
        print str(index)+' : '+site   
    sys.exit(1)

module=options.module

outdir=options.outdir
if not outdir:
    outdir=os.getenv("ND280JOBS")
    if not outdir:
        outdir=os.getenv("PWD") + '/Jobs/'
    outdir+='/'+nd280ver + '/' ## Always add nd280ver to path to keep separate.

if not os.path.isdir(outdir):
    out = commands.getstatusoutput('mkdir ' + outdir)

unmake=options.unmake

forced=options.forced

compile=options.compile

delete=options.delete

beam=options.beam

name=options.name

arglist='-v '+nd280ver
if module:
    arglist+=' -m '+module
if unmake:
    arglist+=' -u '+unmake
if forced:
    arglist+=' -f '+forced
if compile:
    arglist+=' -c '+compile
if delete:
    arglist+=' -d '+delete
if beam:
    arglist+=' -b '+beam
if name:
    arglist+=' -n '+name

jdl_name = outdir + "ND280Install_"+nd280ver+".jdl"
jdlfile = open(jdl_name,"w")
jdlfile.write('Executable = "ND280Software.py";\n')
jdlfile.write('Arguments = "'+arglist+'";\n')
jdlfile.write('InputSandbox = {"../tools/*.py"};\n')
jdlfile.write('StdOutput = "InstallND280.out";\n')
jdlfile.write('StdError = "InstallND280.err";\n')
jdlfile.write('OutputSandbox = {"InstallND280.out", "InstallND280.err"};\n')
jdlfile.write('Requirements = other.GlueCEPolicyMaxCPUTime > 600 && other.GlueHostMainMemoryRAMSize >= 512; \n')

if os.getenv('MYPROXY_SERVER'):
    jdlfile.write('MyProxyServer = \"'+os.getenv('MYPROXY_SERVER')+'\";')
else:
    print 'Warning MyProxyServer attribute undefined!'

jdlfile.close()


nsite =  0
isite = -1
for site in site_list:
    isite += 1

    if ce.isdigit():
        if int(ce) != isite:
            continue
    else:
        if ce != 'all' and site != ce:
            continue

    jid_name=jdl_name.replace('.jdl','_'+str(isite)+'.jid')

    if os.path.isfile(jid_name):
        print 'Removing old jid file'
        outdel = commands.getstatusoutput('rm -rf ' + jid_name)
        if outdel[0] != 0:
            print 'Error: rm -rf ' + jid_name + ' failed'

    #command = 'glite-wms-job-submit -d perkinInstall -c ../processing_scripts/autowms.conf -o ' + jid_name + ' -r ' + site + ' ' + jdl_name
    command = 'glite-wms-job-submit -a -c ../processing_scripts/autowms.conf -o ' + jid_name + ' -r ' + site + ' ' + jdl_name
    print 'Sending install job to: ' + site
    print command
    
    ii=0
    while ii < 1:
        
        child=pexpect.spawn(command,timeout=30)
        ii=child.expect([pexpect.TIMEOUT,pexpect.EOF])
        
        if ii == 0:
            os.system('rm -f ' + jid_name)
            print 'Retrying ...'
        else:
            print child.before
        
        #Give the wms some time
        time.sleep(5)
        
    nsite += 1
        
print '--------------------------------'
print 'Submitted ' + str(nsite) + ' jobs'

