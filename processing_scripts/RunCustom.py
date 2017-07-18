#!/usr/bin/env python

#---------------------------------------------------------------
#Script to submit a custom GRID job
#---------------------------------------------------------------

import sys
import optparse
import ND280GRID
import os
import time
import pexpect
import commands
from ND280GRID import ND280File

#Parser options

usage  = 'usage: %prog [options]'
parser = optparse.OptionParser()

#Mandatory
parser.add_option('-f', '--filename',    default='file.list',    help='File containing filenames to process')
parser.add_option('-v', '--version',     default='v11r31',       help='Version of nd280 software to use')
parser.add_option('-x', '--execfile',    default='MyProcess.py', help='Executable/Script that should be sent with the job')

#Optional
parser.add_option('-n', '--nodatareq',   default=False,          help='Optional disable DataRequirements in JDL file', action='store_true', )
parser.add_option('-o', '--outdir',      default='',             help='Optional output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present')
parser.add_option('-r', '--resource',    default='',             help='Optional CE resource to submit to')
parser.add_option('-u', '--delegation',  default='',             help='Optional proxy delegation id, e.g $USER')
parser.add_option('-O', '--optargs',     default='',             help='Optional arguments passed to executable, comma delimited')
parser.add_option('-i', '--inputs',      default='',             help='Optional files for input SandBox, comma delimited')
parser.add_option('--dirac',             default=False,          help='Optional submission via DIRAC', action='store_true')
parser.add_option('--useTestDB',         default=False,          help='Prepend the DB cascade with test DB', action='store_true')
parser.add_option("--test",              default=False,          help="Test run, do not submit jobs", action='store_true')

(options,args) = parser.parse_args()

###############################################################################

# Main Program

if not os.path.exists(options.filename) or not os.path.exists(options.execfile):
    parser.print_help()
else:
    print 'Running with %s' % (' '.join([options.filename,options.version,options.execfile]))
    
# Abbreviate options
delegation  = options.delegation
execfile    = options.execfile
listname    = options.filename
nd280ver    = options.version
optargs     = options.optargs
outdir      = options.outdir
resource    = options.resource
username    = os.getenv('USER')

# Determine output directory
if not outdir:
    outdir = os.getenv('ND280JOBS')
    if not outdir:
        outdir = os.getenv('PWD') + '/Jobs/'
    outdir += '/' + nd280ver
outdir += '/'

if not os.path.isdir(outdir):
    out = commands.getstatusoutput('mkdir ' + outdir)

# Read input file list
filelist = [ f.strip() for f in open(listname,'r').readlines() ]

# Define arguments to custom process
arglist = '-v '+nd280ver+' -i '
if optargs:
    arglist = arglist + ' ' + ' '.join(options.optargs.split(','))

# Use the test DB?
if options.useTestDB:
    arglist += ' --useTestDB '

# Count the number of jos submitted
counter = 0

# Loop over the list of files to process
for f in filelist:

    # Create file instance
    try:
        infile = ND280File(f)
    except:
        print 'File not on LFN, skipping'
        continue

    runnum    = infile.GetRunNumber   ()
    subrunnum = infile.GetSubRunNumber()
    jdlname   = outdir + 'ND280Custom_' + nd280ver +'_' + runnum + '_' + subrunnum + '.jdl'
    jidname   = jdlname.replace('.jdl','.jid')

    # Open JDL file for writing
    jdlfile = open(jdlname,"w")

    # Write the custom JDL (should use ND280JDL here - but it is presently only capable of handling one extra file for the input sanbox)
    jdlfile.write('Executable = "'+execfile+'";\n')
    jdlfile.write('Arguments = "'+arglist+"'"+f+"'"+'";\n')
    jdlfile.write('InputSandbox = {"../tools/*.py","'+execfile+'","../custom_parameters/*.DAT"')
    if options.inputs:
        for i in options.inputs.split('/'):
            jdlfile.write(',"'+i+'"')
    jdlfile.write('};\n')
    jdlfile.write('StdOutput = "ND280Custom.out";\n')
    jdlfile.write('StdError = "ND280Custom.err";\n')
    jdlfile.write('OutputSandbox = {"ND280Custom.out", "ND280Custom.err"};\n')
    if not options.nodatareq:
        jdlfile.write('DataRequirements = {\n')
        jdlfile.write('[\n')
        jdlfile.write('DataCatalogType = "DLI";\n')
        jdlfile.write('DataCatalog = "'+os.getenv('LFC_HOST')+':8085/";\n')
        jdlfile.write('InputData = {"'+f+'"};\n')
        jdlfile.write(']\n')
        jdlfile.write('};\n')
        jdlfile.write('DataAccessProtocol = "gsiftp";\n')
    jdlfile.write('VirtualOrganisation = "t2k.org";\n')
    jdlfile.write('Requirements = Member("VO-t2k.org-ND280-'+nd280ver+'",other.GlueHostApplicationSoftwareRunTimeEnvironment) && other.GlueCEPolicyMaxCPUTime > 600 && other.GlueHostMainMemoryRAMSize >= 512; \n')

    if os.getenv('MYPROXY_SERVER'):
        jdlfile.write('MyProxyServer = \"'+os.getenv('MYPROXY_SERVER')+'\";')
    else:
        print 'Warning MyProxyServer attribute undefined!'
 
    jdlfile.close()


    #First delete any old jid and jdl file
    if os.path.isfile(jidname):
        print 'jid file exists, removing'
        fjid = open(jidname,'r')
        flines = fjid.readlines()
        joblink = flines[1]
        jar=joblink.split('/')
        jobout=jar[-1]
        jout=outdir + username + '_' + jobout
        if os.path.isfile(jout):
            print 'output file exists, removing'
            outdel = commands.getstatusoutput('rm -rf ' + jout)
            if outdel[0] != 0:
                print 'Error: rm -rf ' + jout + ' failed'
        outdel = commands.getstatusoutput('rm -rf ' + jidname)
        if outdel[0] != 0:
            print 'Error: rm -rf ' + jidname + ' failed'

    if options.dirac:
        command = 'dirac-wms-job-submit ' + jdlname + ' > ' + jidname
    else:
        command = 'glite-wms-job-submit'
        if delegation:
            command += ' -d ' + delegation
        else:
            command += ' -a'
        command += ' -c autowms.conf -o ' + jidname
        if not resource:
            command += ' ' + jdlname
        else:
            command += ' -r ' + resource + ' ' + jdlname
    print command

    ii=0
    trials=0
    while ii < 1 and trials < 10:

        if os.path.isfile(jidname):
            print 'jid written, do not submit again'
            break

        if options.test:
            print 'TEST RUN'
            break

        child=pexpect.spawn(command,timeout=30)
        ii=child.expect([pexpect.TIMEOUT,pexpect.EOF])

        if ii == 0:
            print 'Retrying ...'
            trials += 1
        else:
            print child.before

        #Give the wms some time
        time.sleep(2)

    counter += 1


print '--------------------------------'
print 'Submitted ' + str(counter) + ' jobs'





