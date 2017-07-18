#!/usr/bin/python

from ND280GRID import *
import optparse
import os
import sys
import stat
import time


# limit on the number of parallel processes (LFC I/O)
N_PROC_MAX=5


# define command line options
parser = optparse.OptionParser()

parser.add_option('-f', dest='force', default=0, help='Use to force regeneration of LFC recusive file list')

(options,args) = parser.parse_args()


# make sure we are working in a grid enabled environment
if not os.getenv('LFC_HOME'):
    print 'LFC_HOME is unset, did you source the nd280Computing setup script?'
    sys.exit(1)
else:
    lfcHome = os.getenv('LFC_HOME')


# was the file path specified as an input?
if len(args) != 1:
    print 'Please specify input path!'
    print ' ./lfcDump.py production006/B/mcp'
    sys.exit(1)


# parse the input file path
inputPath = args[0]


# going to write a recursive ls if the input file path to a temporary file
tmpPath = 'dumps/'+inputPath.replace(lfcHome,'').replace('/','.')+'.tmp'


# make sure path exists
lines,errors = runLCG('lfc-ls '+inputPath,is_pexpect=False)
if errors:
    print 'Input path not recognised',inputPath
    sys.exit(1)




# function to write the recursive logical file list
def writeLFCFileList():
    
    command = 'lfc-ls -lR ' + inputPath
    lines,errors = runLCG(command,3600,False)
    
    if errors:
        print 'Failed to recursively ls %s' % (inputPath)
        sys.exit(1)
        
    tmpFile = open(tmpPath,'w')
    tmpFile.write('\n'.join(lines))
    tmpFile.close()




# function to run a (parallel) process for the purpose of determining the replicas of files in a LFC directory
def createLFCOutputs(outputPath,directory,processList):
    
    # lines in the process script - lcg-lr the files in this directory
    lines = [
        '#!/bin/bash',
        'source $ND280COMPUTINGROOT/data_scripts/cronGRID.sh > /dev/null 2>&1', 
        'for file in $(lfc-ls '+directory+'); do ',
        '    echo $file',
        '    lcg-lr lfn:'+directory+'/$file',
        '    echo',
        'done'
        ]
        
    # script for this process
    scriptPath = outputPath.replace('.out','.in')
    script     = open(scriptPath,'w')

    # make it executable
    os.chmod(scriptPath,stat.S_IRWXU)
        
    # write the script
    script.write('\n'.join(lines))
    script.close()

    # open the ouput file for writing
    output = open(outputPath,'w')

    # create a process to execute the script and place in dictionary
    processList.append(subprocess.Popen([scriptPath], stdin=None, stdout=output, stderr=output))

    # dont't submit more than N_PROC_MAX parallel processes
    processWait(processList,N_PROC_MAX)




# function to count the replicas from the output files
def countLFCReplicas(fileList=[]):

    # loop over the list of files containing the replica information
    for fileName in fileList:
        
        # reform directory name from fileName
        dirName = os.path.basename(fileName).replace('.out','').replace('.','/')

        f = open(fileName,'r')
        lines = [ l.strip() for l in f.readlines() ]
        f.close()

        # extract the file names
        names = [ l for l in lines if not l.startswith('srm://') and not ' ' in l and l != '' ]
        
        print '%10d total files in %s' % (len(names),dirName)

        # now look for srm instances
        for se,root in se_roots.iteritems():
            replicas = [ l for l in lines if l.startswith(root) and os.path.basename(l) in names ]
            if replicas:
                print '%10d replicas on %s' % (len(replicas),se)
        
        print ''




def main():

    # does the temporary file already exist?
    if not os.path.exists(tmpPath) or options.force:
        print 'Writing recursive LFC list to %s' % (tmpPath)
        writeLFCFileList()


    # read the file list
    print 'Reading recursive file list from %s' % (tmpPath)
    f = open(tmpPath,'r')
    fileList = [ l.strip() for l in f.readlines() ]
    f.close()


    # extract the list of directories (line endswith ':' and next line isn't empty)
    dirList  = []        # build a list of directories containing files
    thisDir  = ''        # track name of current directory
    isADir   = False     # true if the lines being read belong to a directory
    hasFiles = False     # true if the directory in question has files (and not just directories)
    

    for l in fileList:

        # is this a directory?
        if l.startswith('/grid/') and l.endswith(':'):
            thisDir = l.replace(':','')
            isADir  = True
        
        # does this directory contain files?
        if not hasFiles and isADir and thisDir:
            if not l.startswith('drwx') and l != '' and l.replace(':','') != thisDir:
                hasFiles = True

        # when a blank line is encountered, directory is changed
        if l == '':

            # if this is a directory with files in append it to the list
            if isADir and hasFiles:
                dirList.append(thisDir)

            # reset
            thisDir = ''
            isADir = hasFiles = False
        
    print 'List of directories containing files:'
    print '\n'.join(dirList)


    # going to be running parallel processes for each directory, keep a list of processes
    processList = []
    

    # going to want to read the output files, keep them in a list
    outputList = []


    # for each directory, create a process that determines the replicas for each file
    for directory in dirList:
        
        # output path for this directory
        outputPath = 'dumps/'+directory.replace(lfcHome,'').lstrip('/').replace('/','.')+'.out'
        outputList.append(outputPath)

        # don't recreate output if it already exists, unless forced
        if not os.path.exists(tmpPath) or options.force:
           
            # create outputs
            createLFCOutputs(outputPath,directory,processList)
        else:
            print '%s already exists, use -f 1 option to replace' % (outputPath)

                
    # were any processes submitted?
    if processList:
        print 'Submitted all processes'

        # wait for all  subprocesses to finish
        processWait(processList,0)


    # now, count the replicas
    countLFCReplicas(outputList)

    
    # finish
    sys.exit(0)


if __name__ == "__main__":
    main()
