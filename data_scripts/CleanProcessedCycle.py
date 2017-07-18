#!/usr/bin/env python
"""
Clean Whole Processing Cycle from T2:
"""

import os
import sys
import ND280GRID
import optparse
import subprocess


# Parser Options:
parser = optparse.OptionParser(usage ="""\
usage: %prog [options]

       Clean Whole Processing Cycle from T2:

       Launch script for CleanProcessed.py that archives full production cycles
       according to production directory format via 'nohup nice'. In the case
       of non-production data, one job per subdirectory is run.

Example:
       $./CleanProcessedCycle.py --cycle=production004/A --fts 1 --skip=reco
""")
parser.add_option("--cycle",        type="string", help="Specify processing cycle e.g. production004/A to clean")
parser.add_option("--fts",          type="int",    help="Specify 1 (default) to use FTS 0 to use lcg-cr",                                                                                                                                 default=1)
parser.add_option("--skip",         type="string", help="Skip T2 removal of a file type e.g. reco, can specify ALL")
parser.add_option("--filetags",     type="string", help="'/' delimited list of file tags to archive/clean e.g. reco/cali/anal")
parser.add_option("--type",         type="string", help="Specify production type: rdp (defult) mcp (for all MC or mcp/genie, or mcp/neut for specified generator only) or non (for non production004) and fpp for first pass processing", default="rdp")
parser.add_option("--verify",       type="int",    help="Specify whether to archive verification files (default 0, 1= yes, 2=verification only)",                                                                                         default=0)
parser.add_option("--version",      type="string", help="Specify a version for verification",                                                                                                                                             default='')
parser.add_option("--delete",       type="string", help="'/' delimited list of all file tags to delete e.g. cnfg/unpk/.txt")
parser.add_option("--T1",           type="string", help="Specify RAL (default) or TRIUMF",                                                                                                                                                default='RAL')
parser.add_option("--noTRIUMFToRAL",type="int",    help="Do not copy replicas from TRIUMF to RAL!",                                                                                                                                       default=1)
parser.add_option("--recipient",    type="string", help="send notification email to this recipient",                                                                                                                                      default='j.perkin@shef.ac.uk')  # nd280-grid@mailman.t2k.org
parser.add_option("--noRegDark",    type="int",    help="Skip any attempts to pick up unregistered replicas",                                                                                                                             default=0)
parser.add_option("--pattern",      type="string", help="Specify a substring which directories must match in order to be archived/cleaned",                                                                                               default='')
parser.add_option("--test",         default=False, help="Run the script in test mode",                                                                                                                                                    action='store_true')
(options,args) = parser.parse_args()


## is this a test?
if options.test:
    print "Running in TEST mode!"


## Processing cycle:
if not options.cycle:
    parser.print_help()
    sys.exit(1)


# Resource
resources = 'RAL','TRIUMF'
if options.T1 not in resources:
    print 'Invalid T1 resource'
    parser.print_help()
    sys.exit(1)


## The FTS log directory:
transfer_dir= os.getenv("ND280TRANSFERS")
if not transfer_dir:
    transfer_dir=os.getenv("HOME")


## Processed data root path:
fullpath = '/grid/t2k.org/nd280/'+options.cycle+'/'

## Get the cycle number and integerise as directory structure changes
cyclenum = options.cycle.split('/')[0][-1]
if not cyclenum.isdigit():
    print 'Unrecognised cycle number!',cyclenum
    sys.exit(1)
else:
    cyclenum = int(cyclenum)


## MCP directory structure (all encompassing):
mcp_confs  = ['2010-02-water','2010-11-air','2010-11-water']
mcp_geoms  = ['basket','magnet','sand']
mcp_baskets= ['ccpiplus','ccpizero','ncpiplus','ncpizero','nue','beam']
mcp_beams  = ['beama','beamb','beamc','run1','run2','run3','run4','run5']
mcp_baskets += mcp_beams


mcp_dirs   =[]
## try all possible permutations
for geom in mcp_geoms:
    for conf in mcp_confs:
        if geom == 'basket':
            for basket in mcp_baskets:
                mcp_dirs.append(conf+'/'+geom+'/'+basket)
        else:
            for beam in mcp_beams:
                mcp_dirs.append(conf + '/' + geom + '/' + beam)


## cosmic MCP dirs (production dependent)
cosmic_geoms = ['allcosmic','basecosmic','fgdcosmic','triptcosmic']
cosmic_dirs  = []
for conf in mcp_confs:
    for geom in cosmic_geoms:
        cosmic_dirs.append(conf+'/corsika5F/'+geom)
    

## Processing type:
if (options.type == 'rdp' or options.type == 'fpp' or 'mcp' in options.type) and not 'production' in options.cycle:
    parser.print_help()
    sys.exit(1)

elif options.type == 'non':
    command = 'lfc-ls '+fullpath
    dirs,errors = ND280GRID.runLCG(command,in_timeout=1800)
    if errors: raise Exception

elif options.type == 'calib':
    fullpath = '/grid/t2k.org/nd280/calib/' + options.cycle + '/'
    command = 'lfc-ls ' + fullpath
    dirs,errors = ND280GRID.runLCG(command,in_timeout=1800)
    if errors: raise Exception
    
elif options.type == 'rdp' or options.type == 'fpp':
    dirs = []
    fullpath += options.type+'/'

    if options.verify:
        
        if options.version:
            extrapath = options.version+'/ND280/'
        else:
            extrapath = ''

        ## Get list of verfication directories (if present) and append:
        command = 'lfc-ls '+fullpath+'verify/'+extrapath

        lines,errors = ND280GRID.runLCG(command,in_timeout=1800)
        if errors:
            print '\n'.join(errors)
            print 'No verification'
        else:
            dirs = ['verify/'+extrapath+line for line in lines]

    if options.verify < 2:
        ## Get list of run directories:
        print 'Get list of run directories...'
        command = 'lfc-ls '+fullpath+'ND280/'
        lines,errors = ND280GRID.runLCG(command,in_timeout=1800)
        if errors:
            print 'No rdp files yet'
        else:
            dirs2 = ['ND280/'+ line for line in lines]
            dirs += dirs2
            print 'dirs:',dirs
    else :
        print 'Verification only archive/cleanup!'

elif 'mcp' in options.type:
    fullpath +='mcp' + '/'
    veri_dirs  = []
    dirs       = []

    # determine verification directories first
    if options.verify:

        if options.version:
            extrapath = options.version+'/'
        else:
            extrapath = ''
            
        command = 'lfc-ls '+fullpath+'verify/'+extrapath

        lines,errors = ND280GRID.runLCG(command,in_timeout=1800)
        if errors:
            print '\n'.join(errors)
            print 'No verification'
        else:
            # veri_dirs = ['verify/'+extrapath+line for line in lines]
            if 'neut' in options.type or 'genie' in options.type:
                dirs  = ['verify/'+extrapath+options.type.replace('mcp/','')+'/'+mcp_dir for mcp_dir in mcp_dirs]
            elif options.type == 'mcp/cosmic':
                dirs = ['verify/'+extrapath+'cosmic/'+cosmic_dir for cosmic_dir in cosmic_dirs]
            else:
                genie_dirs = ['verify/'+extrapath+'genie/'+mcp_dir for mcp_dir in mcp_dirs]
                neut_dirs  = ['verify/'+extrapath+'neut/'+mcp_dir for mcp_dir in mcp_dirs]
                dirs = genie_dirs + neut_dirs

    # append production directories
    if 'mcp' in options.type and options.verify < 2:
        genie_dirs = ['genie/' + mcp_dir for mcp_dir in mcp_dirs]
        neut_dirs  = ['neut/'  + mcp_dir for mcp_dir in mcp_dirs]
        if 'neut' in options.type or 'genie' in options.type:
            dirs = dirs + [options.type.replace('mcp/','')+'/'+mcp_dir for mcp_dir in mcp_dirs]
        else:
            dirs = dirs + genie_dirs + neut_dirs

    # or, is this comsics?
    elif options.type == 'mcp/cosmic' and options.verify < 2:
        # 4/C cosmic directory structure...
        sub1 = ['corsikanew','corsikanew_nomag']
        sub2 = ['all','base','fgd','tript']
        dirs = []
        for s1 in sub1:
            for s2 in sub2:
                dirs.append('cosmic/2010-11-water/'+s1+'/'+s2+'cosmic')

    elif options.type != 'mcp' and options.verify < 2:
        dirs = dirs + [options.type.replace('mcp','') + mcp_dir for mcp_dir in mcp_dirs]
    else:
        print 'Verification only archive/cleanup!'

else:
    print 'Unrecognised type : ' + options.type
    sys.exit(1)


## Submit one CleanProcessed job per run directory
for run_dir in dirs:
    run_dir = ND280GRID.rmNL(run_dir)

    ## don't submit if path doesn't exist
    command = 'lfc-ls ' + fullpath + run_dir
    if options.test:
        print 'Checking path:',command
    p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if not p.stdout.readlines():
        if options.test:
            print 'Failed',command
        continue

    ## Log file
    log_end = run_dir.rstrip('/').replace('/','_')+'_'+options.type.replace('/','_')+'_'+options.T1
    log = transfer_dir+'/clean_'+options.cycle.replace('/','_')+'_'+log_end+'.log'

    ## Run nicely via nohup
    command = 'nohup nice ./CleanProcessed.py --T1 '+options.T1

    ## Pass through optional args
    if     options.fts:           command += ' --fts='          +str(options.fts)
    if     options.skip:          command += ' --skip='         +options.skip
    if     options.filetags:      command += ' --filetags='     +options.filetags
    if     options.delete:        command += ' --delete='       +options.delete
    if not options.noTRIUMFToRAL: command += ' --noTRIUMFToRAL='+str(options.noTRIUMFToRAL)
    if     options.recipient:     command += ' --recipient='    +options.recipient
    if     options.noRegDark:     command += ' --noRegDark='    +str(options.noRegDark)

    ## Add full path and log file
    command += ' --fullpath='+fullpath+run_dir+'  >'+log+' 2>'+log+' &'

    ## Skip early (unprocessed) data directories
    isToSkip = False
    earlies = ['0000'+str(i)+'999' for i in xrange(4)]
    for early in earlies:
        if early in fullpath+run_dir:
            isToSkip=True

    ## skip directories not matching desired pattern
    if options.pattern:
        if options.pattern not in fullpath+run_dir:
            isToSkip=True

    if not isToSkip:
        ## Execute command
        print command
        if not options.test:
            os.system(command)
