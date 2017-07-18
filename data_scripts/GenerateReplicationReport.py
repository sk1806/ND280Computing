#!/usr/bin/env python

"""
Generate a report of where files in an LFC data directory are registered from.

The LFC directory can specified in a number of ways:
     lfn:/grid/t2k.org/nd280/raw/ND280/ND280/0000*000_0000*999/
would search the specified run number only, whereas:
     lfn:/grid/t2k.org/nd280/raw/ND280/ND280/
would descend into all the runs in that directory.
     lfn:/CURRENT
determines the current raw data directory and uses that.

Currently the SRM options are T1 or ALL.

jonathan perkin 20110203

"""

from ND280GRID import ND280File, ND280Dir
import ND280GRID
import optparse
import os
import sys
import traceback
import time
import datetime
from datetime import date


def DirectoryReport(report,LFCDir,SRMS,srm_opt=''):

    # Zero the file counters
    SRMCount = {}
    for srm in SRMS:
        SRMCount[srm]=0
    
    # Now, I can access the registers for each file in each subdirectory.
    # Want to count how many of the files are registered at each SE
    lfcFileCount = 0

    # Print directory
    output = LFCDir.dir+'\n'
    print output
    report.append(output)
    
    
    for LFCFile in  LFCDir.ND280Files:
        ## Uniquify replicas (shouldn't be more than one per SRM anyway!)
        replicas = list(set(LFCFile.reps))
        
        ## Count LFC entries
        lfcFileCount += 1
        
        ## Count SRM replicas
        for rep in replicas:
            srm = ND280GRID.GetSEFromSRM(rep)
            if srm in SRMCount.keys():
                SRMCount[srm] += 1

    # Add info about how many files are at KEK
    KEKCount = ND280GRID.GetNRawKEKFiles(LFCDir.dir)
    if KEKCount:
        output  = '%-35s: %4d/%4d replicas\n' % ('KEK HPSS',KEKCount,lfcFileCount)
    else:
        output = "Couldn't find KEK files\n"
    print output
    report.append(output)

    # SRM info
    for srm in SRMS:
        # Only non zero entries
        if SRMCount[srm]:
            output = '%-35s: %4d/%4d replicas\n' % (srm,SRMCount[srm],lfcFileCount)
            print output
            report.append(output)

    # For T2 reports, write how many files are in GoodRuns.list for
    # comparison
    if srm_opt == "ALL":
        output = '%-35s: %4d/%4d replicas\n' % ('Number of good run files',ND280GRID.GetNGoodRuns(LFCDir.dir),lfcFileCount)
        print output
        report.append(output)

    # Write newline
    report.append('\n')


# Parser Options
parser = optparse.OptionParser()
parser.add_option("-l","--lfcdir",dest="lfcdir",     type="string",help="lfc directory to report")
parser.add_option("-s","--srmopt",dest="srmopt",     type="string",help="srms to report")
parser.add_option("-r","--report",dest="report_path",type="string",help="report file path")
(options,args) = parser.parse_args()


def GenerateReplicationReport():
    
    # The start time.
    start = time.time()

    # keep track of failed directories
    failures = []

    # Parse LFC directory name
    lfc_dir_name = options.lfcdir
    if not lfc_dir_name or not 'lfn:/' in lfc_dir_name:
        sys.exit('Please state the LFC directory to report, using the -l or --lfcdir switch')
    if lfc_dir_name == "lfn:/CURRENT":
        print 'Finding current data directory'
        raw_data_path = ND280GRID.GetCurrentRawDataPath()
        if raw_data_path is None:
            sys.exit('GetCurrentRawDataPath() returned None')
        else: 
            lfc_dir_name = 'lfn:/grid/t2k.org' + raw_data_path


    # Parse SRM option
    srm_opt = options.srmopt
    if srm_opt == "ALL" or srm_opt == "T1":
        print 'srm_opt = '+srm_opt
    else:
        sys.exit('Please use one of the supported SRM options: T1 or ALL, using the -s or --srmopt switch')


    # Today's date.
    datestring =  date.today().isoformat()


    # Get the list of SRMS to query.
    if srm_opt == "ALL":
        SRMS = ND280GRID.GetListOfSEs()
    elif srm_opt == "T1":
        SRMS =      ['t2ksrm.nd280.org','srm-t2k.gridpp.rl.ac.uk']
        DETECTORS = ND280GRID.ND280DETECTORS
    else:
        SRMS = []

    # Sort the SRMS
    SRMS.sort()


    # Keep the report in a list
    report = []


    # Welcome message
    report.append('Generating '+srm_opt+' File Replication Report for '+time.asctime()+'\n\n')


    # Create the ND280Dir object(s) and generate report(s)
    LFCDir = ND280Dir(lfc_dir_name,skipFailures=True)

    # A T2 style report, one for each raw/ND280/ND280 subdirectory
    if "raw/ND280/ND280" in lfc_dir_name and srm_opt == "ALL":
        for subFile in LFCDir.ND280Files:
            try:
                LFCSubDir = ND280Dir(subFile.LFN(),skipFailures=True)
                DirectoryReport(report,LFCSubDir,SRMS,srm_opt)
            except:
                report.append("Couldn't create ND280Dir object for "+subFile.LFN()+'\n')
                report.append(traceback.print_exc())
                failures.append(subFile.LFN())

    # A T1 style report
    elif "T1" in srm_opt and "CURRENT" in options.lfcdir:
        for detector in DETECTORS:
            try:
                path = 'lfn:/grid/t2k.org'+ND280GRID.GetCurrentRawDataPath(detector)
                LFCSubDir = ND280Dir(path,skipFailures=True)
                DirectoryReport(report,LFCSubDir,SRMS,srm_opt)
            except:
                report.append("Couldn't create ND280Dir object for "+path+'\n')
                report.append(traceback.print_exc())
                failures.append(path)


        #include INGRID
        LFCSubDir = ND280Dir('lfn:/grid/t2k.org'+ND280GRID.GetCurrentRawDataPath('INGRID','INGRID'),skipFailures=True)
        DirectoryReport(report,LFCSubDir,SRMS,srm_opt)

    # A generic report for specified directory:
    else:
        try:
            DirectoryReport(report,LFCDir,SRMS)
        except:
            report.append(traceback.print_exc())


    # The time taken
    duration = time.time() - start

    # Write any failed directories
    if len(failures):
        report.append('Dumping list of failures:')
        report.append('\n'.join(failures)+'\n')
    report.append('It took '+str(duration)+' seconds to generate this report.\n\n')

    # The report file
    transfer_dir = os.getenv("ND280TRANSFERS")
    if options.report_path:
        report_name = options.report_path
    else:
        report_name  = transfer_dir+'/replication.'+srm_opt+'.'+datestring.replace('-','')+'.log'
    report_file = open(report_name,"a")
    for line in report:
        report_file.write(line)
    report_file.close()

    # Copy report to web
    command="cp -f "+report_name+" /opt/ppd/t2k/users/stewartt/t2k_logs/www/replication/"
    os.system(command)



if __name__=='__main__':
    GenerateReplicationReport()
