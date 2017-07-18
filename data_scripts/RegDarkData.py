#!/usr/bin/env python

"""
A script to register file replicas not already entered into the
LFC for each SRM specified. Note: SRM files that do not have replicas
already in the LFC will not be registered.

Example usage:
     $ ./RegDarkData.py \
     -l lfn:/grid/t2k.org/nd280/raw/ND280/ND280/00000000_00000999/ \
     gfe02.grid.hep.ph.ic.ac.uk t2ksrm.nd280.org

Currently works on explicit filename only, want to add other features such as:
- file permissions
- checksumming

Any other suggestions please e-mail me, b.still@qmul.ac.uk
Further modifications j.perkin@shef.ac.uk
"""

from ND280GRID import *
import optparse
import os
import sys
import time
import pexpect
import traceback

# Parser Options
parser = optparse.OptionParser()
parser.add_option("-l","--lfcdir",  dest="lfcdir",  type="string",help="lfc directory to use for search")
parser.add_option("-f","--filelist",dest="filelist",type="string",help="name of file containing list of LFNs to register")
(options,args) = parser.parse_args()

###############################################################################
# Main Program

def main():
    # The start time.
    start = time.time()

    # Parse LFC directory name
    lfc_dir_name   = options.lfcdir
    file_list_name = options.filelist
    if (not lfc_dir_name and not file_list_name) or (lfc_dir_name and not 'lfn:' in lfc_dir_name) or (lfc_dir_name and file_list_name):
        parser.print_help()
        sys.exit('Please state an lfc directory OR provide a list of LFNs to use for the dark data search using the -l or --lfcdir flag')

    # Parse SRMs
    srms=[]
    if args:
        for a in args:
            srms.append(a)
    if not srms:
        sys.exit('Please state at least one srm to use for dark data search, as arguments')

    # Create an ND28Dir object, automatically instantiating an ND280File
    # object for those files contained therin if a directory is specified
    if lfc_dir_name:
        print 'Creating ND280Dir object for ',lfc_dir_name
        lfc_dir   = ND280Dir(lfc_dir_name,skipFailures=True)
        lfc_files = lfc_dir.ND280Files

    # Keep a list of files that threw an exception
    exception_files = []

    # Alternatively create an ND280File instance for each LFN in the file 
    # provided
    if file_list_name:
        print 'Creating ND280File list from ',file_list_name
        f         = open(file_list_name,'r')
        names     = [rmNL(name) for name in f.readlines()]
        lfc_files = []
        for name in names:
            try:
                lfc_files.append(ND280File(name,check=False))
            except:
                exception_files.append(name)

    # Keep a list of files with null size
    null_size_files = []

    # Keep a list of files with bad or no checksums
    bad_checksum_files = []
    no_checksum_files  = []


    # Loop over all the files in the specified LFC directory
    for f in lfc_files:

        try:
        
            # skip directories:
            if f.is_a_dir:
                print f.alias+' is a directory, skipping!'
                continue

            # keep a list of replica checksums, the first replicas has the definitive
            # checksum
            checksums = []
            for rep in f.reps:
                lines,errors = runLCG('lcg-get-checksum '+rep)
                if lines and not errors:
                    cs = lines[0].split()[0]
                    if cs not in checksums and cs != '(null)':
                        checksums.append(cs)
                    
            if len(checksums)>1:
                bad_checksum_files.append(f.alias)
            elif not checksums:
                no_checksum_files.append(f.alias)


            # Loop over all SRMs
            for srm in srms:

                # First see if file is already registered from this srm
                surl_file_name,registered_surl=f.SURL(srm)

                if registered_surl and (srm in surl_file_name):
                    print f.alias + ' is on the LFC, registered from ' + surl_file_name
                    continue                

                # Try and register the file
                command= 'lcg-rf --vo t2k.org -g ' + f.guid + ' ' + surl_file_name
                lines,errors = runLCG(command)
                print "\n".join(lines)

                # Did it register?
                isRegistered = False
                if lines:
                    if 'guid' in lines[0]:
                        isRegistered =  True

                # Consistency checking...


                # If the file successfully registered, then it is legit, 
                # but make sure file size is not zero, otherwise delete this
                # instance
                command = 'lcg-ls -l ' + surl_file_name
                lines,errors = runLCG(command)

                if lines and not errors:
                    surl_size = int(lines[0].split()[-3])

                    if surl_size == 0:
                        print surl_file_name + ' has null size! Deleting...'
                        null_size_files.append(surl_file_name)

                        command = 'lcg-del ' + surl_file_name
                        runLCG(command)


                # Does the replica exsits?
                if isRegistered or surl_file_name in f.reps:

                    # If the lcg-ls threw a 'No such file error'
                    # (usually due to failed FTS transfer), unregister it
                    for error in errors:
                        if 'No such file' in error:
                            print surl_file_name + ' does not exist!'
                            command = 'lcg-uf --vo t2k.org ' +f.guid + ' ' +surl_file_name
                            runLCG(command)
                            break
                                
                                
                    # Make sure checksum matches definitive otherwise delete this instance
                    if checksums:
                        command = 'lcg-get-checksum ' + surl_file_name          
                        lines,errors = runLCG(command)
                        if lines and not errors:
                            cs = lines[0].split()[0]
                            if cs != checksums[0]:
                                print surl_file_name + ' has bad checksum!'

                                command = 'lcg-del ' + surl_file_name
                                runLCG(command) 
                    else:
                        print f.alias + ' has no checksum!'

            # Dump list of checksums
            print 'checksum list:' + repr(checksums)
                            
        except:
            # Print exception, record duff file and carry on with remaining files...
            traceback.print_exc()
            exception_files.append(f.alias)
                        
    # The time taken
    duration = time.time() - start
    print 'It took '+str(duration)+' seconds to register the data.\n'
    

    # Display any errors...
    for list,description in ((null_size_files,   'null size files'   ),
                             (bad_checksum_files,'bad checksum files'),
                             (no_checksum_files, 'no checksum files' ),
                             (exception_files,   'exception_files'   )):
        if len(list):
            print 'Dumping list of '+description+':'
            print "\n".join(list)


if __name__=='__main__':
    main()
