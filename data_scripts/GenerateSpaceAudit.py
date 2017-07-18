#!/usr/bin/env python

"""
Generate a report of which files in the LFC are replicated where
Information will be stored in a ROOT::TTree
Note can use Entry$ syntax in TTree::Draw() later for integrating sizes
To scan long fields, use tree->Scan("name","","colsize=30")

jonathan perkin 20120911

"""

from   ROOT import *
import ND280GRID
import optparse
import os
import sys
import traceback
import time
from datetime import date

# parser options
nd280SRMs = ND280GRID.GetListOfSEs()
lfcRoot   = os.getenv('LFC_HOME')
rootName  = sys.argv[0].replace('.py','.root')
usage     = "usage: %prog [options]"
parser    = optparse.OptionParser(usage=usage)
parser.add_option("--lfcDir",    default=lfcRoot,   help="LFC directory to audit")
parser.add_option("--srmList",   default=nd280SRMs, help="',' delimited list: SRMS to audit")
parser.add_option("--hasInPath", default=[],        help="',' delimited list: only match files with this string in their path")
parser.add_option("--notInPath", default=[],        help="',' delimited list: only match files without this string in their path")
parser.add_option("--rootName",  default='',        help="output file name")
parser.add_option("--reportName",default='',        help="report file path")
(options,args) = parser.parse_args()

if options.lfcDir == lfcRoot:
    print 'Are you sure you want to audit the whole LFC in one go?!'
    choice = raw_input('Answer y/n: ')
    if choice == 'y' : pass
    else: sys.exit(1)

# units
toGB = 1024*1024*1024

class AuditInfo:
    """
    Object to encapsulate the pertinent space auditing information.
    Owns a ROOT::TTree to which file paths, replicas, sizes etc
    are saved.
    """
    
    def __init__(self):
        
        # date and time info
        self.startTime = time.time()
        self.date      = date.today().isoformat()
        self.duration  = ''

        # file paths
        transferDir = os.getenv("ND280TRANSFERS")
        if options.reportName:
            self.reportName = options.reportName
        else:
            self.reportName = transferDir+'/spaceAudit'+options.lfcDir.replace(lfcRoot,'').replace('/','.')+'.'+self.date.replace('-','')+'.log'

        if not options.rootName:
            self.rootName = self.reportName.replace(self.reportName.split('.')[-1],'root')
        else:
            self.rootName = options.rootName

        # open ROOT file (for disk resident) TTree
        self.rootFile = TFile.Open(self.rootName,'RECREATE')
        
        # store ND280File info, use vectors for containers
        self.name  = std.vector('string')()
        self.alias = std.vector('string')()
        self.guid  = std.vector('string')()
        self.reps  = std.vector('string')()
        self.srms  = std.vector('string')()
        self.size  = std.vector('long'  )()

        # plant TTree to contain file info
        self.tree = TTree("fileTree","fileTree")

        # grow branches
        self.tree.Branch("name", self.name)
        self.tree.Branch("alias",self.alias)
        self.tree.Branch("guid", self.guid)
        self.tree.Branch("reps", self.reps)
        self.tree.Branch("srms", self.srms)
        self.tree.Branch("size", self.size)

        # a list of lines containing the report summary
        self.report = []

        # a list of the subdirectories being audited
        self.subdirectories = []

        # inline counters
        self.totalSize  = 0
        self.totalFiles = 0
        self.srmSize    = {}
        for srm in options.srmList: 
            self.srmSize[srm] = 0 


    # function to clear vectors
    def ClearVectors(self):
        self.name .clear()
        self.alias.clear()
        self.guid .clear()
        self.reps .clear()
        self.srms .clear()
        self.size .clear()


    # method to write report file and tree
    def Write(self):

        reportFile = open(self.reportName,"w")
        for line in self.report:
            reportFile.write(line)
        reportFile.close()

        self.tree    .Write()
        self.rootFile.Close()

        # delete empty ROOT files
        if not self.tree.GetEntriesFast():
            output = 'No entries in', self.tree.GetName()+'\n'
            print output
            self.report.append(output)
            if os.path.exists(self.rootName):
                output = 'Removing', self.rootName+'\n'
                print output
                self.report.append(output)
                os.remove(self.rootName)
            else:
                output = self.rootName, 'not found\n'
                self.report.append(output)
                

    # print method
    def Print(self):
        for attr,value in sorted(self.__dict__.iteritems()):
            if 'object '   in repr(value): continue
            if 'instance ' in repr(value): continue
            print '%10s: %s' %(attr,value)
            

    # the auditing method
    def Audit(self):
        """
        The auditing method
        """

        # build a list of file paths (can be a bit time consuming)
        command = 'lfc-ls -R '+options.lfcDir
        lines,errors = ND280GRID.runLCG(command,864000) # increase timeout to 24 hrs
        if errors: raise Exception('Failed to recursively list'+options.lfcDir)
    
        # determine the data directories
        output = 'Determining data directories from '+str(len(lines))+' file paths\n'
        print output
        self.report.append(output)
        for i in xrange(1,len(lines)-2):
            # parse the subdirectories by selecting trailing ':'
            if len(lines[i-1]) == 0 and lines[i][-1:]==':' and not '\r' in lines[i]:
                if options.hasInPath:
                    if False in [inPath in lines[i] for inPath in options.hasInPath.split(',')]:
                        continue
                if options.notInPath:
                    if True  in [inPath in lines[i] for inPath in options.notInPath.split(',')]:
                        continue
                self.subdirectories.append(lines[i].replace(':',''))
                                           
        #self.report.append('\n'.join(self.subdirectories))

        # welcome message
        output = 'Generating Space Audit on '+time.asctime()+' for SRMs:\n'+'\n'.join(options.srmList)+'\n\n'
        print output
        self.report.append(output)

        # create the ND280Dir object(s) and generate report(s)
        for subdir in self.subdirectories:
            output = 'Creating ND280Dir object for %s\n' % subdir
            print output
            self.report.append(output)
            thisDir = ND280GRID.ND280Dir('lfn:'+subdir,skipFailures=True)

            # print directory
            output = thisDir.dir+'\n'
            print output
            self.report.append(output)
        
            # loop over files in thes directory
            for thisFile in  thisDir.ND280Files:

                # clear vectors
                self.ClearVectors()

                # store file attributes, but not for directories
                if not thisFile.is_a_dir:
                    for rep in thisFile.reps:
                        srm = rep.replace('srm://','').split('/')[0]
                    
                        if srm in options.srmList:
                            self.reps.push_back(rep)
                            self.srms.push_back(srm)
                            self.srmSize[srm] += thisFile.size

                    # don't save info for this file if reps aren't in srmList
                    if self.srms.size():
                        self.name .push_back(thisFile.filename)
                        self.alias.push_back(thisFile.alias)
                        self.guid .push_back(thisFile.guid)
                        self.size .push_back(thisFile.size)

                        # inline counters
                        self.totalSize  += thisFile.size
                        self.totalFiles += 1

                        # fill the tree
                        self.tree.Fill()

        # the time taken
        self.duration = time.time() - self.startTime  
        output = 'It took %s seconds to generate this space audit\n' % self.duration
        output += 'for LFC path %s\n' % options.lfcDir
        print output
        self.report.append(output)

        # srm size summary
        output = ''
        for srm,size in self.srmSize.iteritems():
            output += '%30s %10d GB\n' % (srm,size/toGB)
        print output
        self.report.append(output)
        
        # total size and number of files
        output = 'There were %d files amounting to %d bytes in total\n' % (self.totalFiles, self.totalSize)
        print output
        self.report.append(output)


def main():

    # create an instance of the auditing info 
    audit = AuditInfo()
    
    try:
        # run the audit
        audit.Audit()
        
    except:
        lines  = 'Space audit failed with exception:'
        lines += traceback.format_exc()
        audit.report.append(lines)
        
    # write the report file and the ROOT file
    audit.Write()



if __name__=='__main__':
    main()
