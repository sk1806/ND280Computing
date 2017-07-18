#!/usr/bin/env python
"""
Skim and process raw data files from the last N days with LITest - to be run every 2 days by CRON
"""

from ND280GRID import *

NDAYSLOOKBACK=30

LISTNAME='raw%d.list' % (NDAYSLOOKBACK)      # the name of the file that will contain the list of raw LFNs to process
ND280VER='v11r31'                            # the version of the nd280 software that will be used

# get the list of raw files from the past N days...
fileList = GetNDaysRawFileList(NDAYSLOOKBACK)

# make sure the files aren't already skimmed
fileList = [ f for f in fileList if os.system('lfc-ls ' + f.replace('lfn:','').replace('raw','contrib/perkin/'+ND280VER).replace('.daq','.skim')) ]
print 'There are %d files to process' % (len(fileList))

# write file list
listFile = open(LISTNAME,'w')
listFile.write('\n'.join(fileList))
listFile.close()

# execute RunCustom.py
command = 'source '+os.getenv('ND280COMPUTINGROOT')+'/data_scripts/cronGRID.sh;'
command += './RunCustom.py -f '+LISTNAME+' -v '+ND280VER+' -x LIProcess.py'
print command
os.system(command)

# write the list of files to be downloaded by download script
downloadFile = open('lidownload.list','w')
downloadList = [ f.replace('raw','contrib/perkin/v11r31').replace('daq.mid.gz','litest.root') for f in fileList ]

# also copy the skim files (20160212)
downloadList += [ f.replace('litest.root','skim.mid.gz') for f in downloadList[:] ]
downloadFile.write('\n'.join(downloadList))
downloadFile.close()

# remove list file after processing
os.remove(LISTNAME)
