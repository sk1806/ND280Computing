#!/usr/bin/env python

"""
Since neutSetupSubmit.py, generates multiple runs and subruns for the given list of input flux files, in order to resubmit
failed and/or missing jobs it is necessary to check the job statuses (if the JID exists) and/or query the LFC for the
expected output. A filesize check is performed if the output is found in the LFC, since aborted/killed jobs can produce
truncate numc files.

This script relies on the JDL being present for the original jobs. If it isn't, neutSetupSubmit.py can be re-run in order
to regerate the JDL without re-submitting *all* the jobs from scratch.
"""

from ND280GRID import *
from glob import glob

if len(sys.argv) == 2:
    jidDir = sys.argv[1]
else:
    print 'Please specify path to JID/JDL files'
    sys.exit(1)

if not jidDir.endswith('/'):
    jidDir = jidDir + '/'

# numc files less than this limit are deemed to be failures
FILESIZELIMIT=500000

# look for the JDL files
jdlList = glob(jidDir+'ND280MC*fluka*.jdl')

# beginning of the job submission command
submitCommand = 'time -p glite-wms-job-submit -a -c autowms.conf'

# LFC output run-subrun tags : (fileSize,fileName)
lfcOutputTagDict = {}

# keep a track of failures
jdlFailures = []

# count hpw many jobs were resubmitted - it's nice to see
nResubmitted = 0

# loop over JDL files, looking for corresponding JID. If there's a JID, check the status. 
# Also check LFC for output (need to read JDL to determine where output should be)
for jdl in jdlList:

    # lazy exception handling
    try:

        # does JID exist?
        if os.path.exists(jdl.replace('.jdl','.jid')):

            print 'Found JID for ', jdl
            jid = ND280JID(jdl.replace('.jdl','.jid'))

            # check status
            print 'Status is ', jid.GetStatus()
            if (not jid.IsRunning() and not jid.IsScheduled and not jid.IsExitClean()) or jid.GetStatus() == 'Aborted':
                
                print 'Resubmitting ' + jid.jidfilename
                os.remove(jid.jidfilename)
                command = submitCommand + ' -o ' + jid.jidfilename + ' ' + jdl
                print command
                os.system(command)
                nResubmitted += 1
            
            if jid.IsDone() and jid.IsExitClean():
                print 'Job exited cleanly, continuing...\n'
                continue

            if jid.IsRunning() or jid.IsScheduled():
                print 'Job is %s, continuing\n' % (jid.GetStatus())
                continue

            if jid.GetStatus() == 'Cleared':
                print 'Job is cleared, checking for output...'
                pass
            # end of status check

        # JID doesn't exist, or job has been cleared from WMS, is there output in the LFC?
        # first extract the job arguments from the JDL, they hold the info required in order to query
        # the LFC...
        jdlLines = [ l.strip() for l in open(jdl).readlines() ] 
        argLine = ''
        for l in jdlLines: 
            if l.startswith('Arguments'):
                argLine = l.lstrip('Arguments = "')
                break
        if not l:
            raise ValueError('Arguments not found')
        # JDL arguments extracted.

        # transliterate arguments into the expected output path...
        argWords = argLine.split(' ')
        argDict = {'version':'', 'evtype':'', 'prod':'', 'type':'', 'generator':'', 'geometry':'', 'vertex':'', 'beam':''}
        for i,w in enumerate(argWords):
            if w == '-v' or w == '--version'   : argDict['version']   = argWords[i+1]
            if w == '-e' or w == '--evtype'    : argDict['evtype']    = argWords[i+1]
            if w == '-p' or w == '--prod'      : argDict['prod']      = argWords[i+1]
            if w == '-t' or w == '--type'      : argDict['type']      = argWords[i+1]
            if w == '-g' or w == '--generator' : argDict['generator'] = argWords[i+1]
            if w == '-a' or w == '--geometry'  : argDict['geometry']  = argWords[i+1]
            if w == '-y' or w == '--vertex'    : argDict['vertex']    = argWords[i+1]
            if w == '-w' or w == '--beam'      : argDict['beam']      = argWords[i+1]
        for a,v in argDict.iteritems():
            if not v or v.startswith('-'):
                raise ValueError('bad %s argument value : %s ' % (a,v))
        outputPath  = 'production%03d' % (int(argDict['prod'][0]))
        outputPath += '/' + argDict['prod'][1] + '/' + argDict['type'] + '/' + argDict['generator'] + '/' + argDict['geometry']
        outputPath += '/' + argDict['vertex']  + '/' + argDict['beam'] + '/numc'

        # only query the LFC once, populate a dictionary of tag:fileSize,fileName
        if not lfcOutputTagDict:

            lfcOutputList,errors = runLCG('lfc-ls -l %s ' % (outputPath), is_pexpect=False)
            if errors : raise ValueError('Unable to lfc-ls -l %s' % (outputPath))

            for line in lfcOutputList:
                words = line.split()

                # fileName is 8th field, fileSize is 4th { tag : (fileSize,fileName) }
                lfcOutputTagDict[ words[8].split('_')[3] ] = (int(words[4]), words[8])

        # parse run-subrun tag from JDL name 
        tag = jdl.rstrip('.jdl')[-13:].replace('_','-')

        # have the vectors for this run-subrun been generated?
        if tag in lfcOutputTagDict:
            fileSize, fileName = lfcOutputTagDict[tag]

            # make sure fileSize is appropriate
            if fileSize > FILESIZELIMIT:
                print '%s has been successfully processed (%d bytes)\n' % (jdl,fileSize)
                continue

            # failed file size check
            print '%s has a suspiciously small size : %d deleting this file...' % (fileName,fileSize)
            lfcFilePath = 'lfn:' + os.getenv('LFC_HOME') + '/' + outputPath + '/' + fileName
            f = ND280File(lfcFilePath)
            command = 'lcg-del -v --vo t2k.org -a '+f.alias
            os.system(command)


        # resubmit if you get to here...
        print 'Resubmitting %s' % (jdl)
        command = submitCommand + ' -o ' + jdl.replace('.jdl','.jid') + ' ' + jdl
        print command
        os.system(command)
        nResubmitted += 1
        
    except:
        traceback.print_exc()
        print 'Failed to submit ',jdl
        jdlFailures.append(jdl)
        continue

if jdlFailures:
    print 'List of failures'
    print '\n'.join(jdlFailures)

if nResubmitted:
    print '%d jobs sucessfully resubmitted' % (nResubmitted)
    print '%d jobs failed to resubmit'      % (len(jdlFailures))




