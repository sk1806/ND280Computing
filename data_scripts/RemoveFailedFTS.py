#!/usr/bin/env python

"""
A script to be run by cron that removes Failed FTS jobs from the queue.

Queries files of the form $ND280TRANSFERS/transfers*log for FTS job IDs.
Uses glite-transfer-status to determine no. of active, finished and failed files.
For each ID, if there are no active files, only failures the transfer is canceled.
A list of the failures is then written to a failure log

jonathan perkin 20110215
"""

from ND280GRID import *
import os
import sys


try:
    ## Look in the transfer directory and list transfer logs, most recent first
    transfer_dir = os.getenv("ND280TRANSFERS")
    lines,errors = runLCG("ls -1 "+transfer_dir+"/transfers.*.log",is_pexpect=False)
    if errors: raise Exception("Couldn't read transfer log")
except:
    print "Unexpected error:", sys.exc_info()[0]
    print '\n'.join(errors)


log_names=[rmNL(line) for line in lines]
    
## Get the transfer logs
for log_name in log_names:
    print '\nExamining '+log_name
    log_file = open(log_name,'r')
    id_list  = log_file.readlines()
    log_file.close();
        
    ## Delete empty log files
    if not len(id_list):
        print 'Removing empty log file:'+ log_name
        if os.path.exists(log_name):
            os.remove(log_name)
        continue

    ## Failure log
    fail_name = log_name.replace('transfers','failures/failures')
    fail_file = open(fail_name,'w')

    # Completed log
    comp_name = log_name.replace('transfers','completed/completed')
    comp_file = open(comp_name,'w')
                
        
    ## Loop over id_list
    for id in id_list:
        print 'ID=',id
            
        ## Count FTS statuses
        n_active   = 0
        n_failed   = 0
        n_finished = 0
            
        try:
            ## The full list of file statuses
            command = "glite-transfer-status -l -s $FTS_SERVICE "+rmNL(id)
            lines,errors = runLCG(command,in_timeout=120,is_pexpect=False)
            if errors:
                if 'was not found' in errors[0]:
                    print rmNL(id)+" no longer on FTS queue"
                
                    ## Remove ID from list
                    print 'removing '+rmNL(id)+' from list'
                    id_list.remove(id)
                    print repr(id_list)
                    comp_file.write(rmNL(id)+': Completed\n')
                    continue
                else: raise Exception("Couldn't get transfer statuses")

            ## Check to see if any files are still active
            source     =''
            destination=''
            state      =''
            reason     =''

            for line in lines:
                if len(line) > 1:
                       
                    if line.split()[0] == 'Source:':
                        source = line.split()[1]
                    
                    if line.split()[0] == 'Destination:':
                        destination = line.split()[1]
                    
                    if line.split()[0] == 'State:':
                        state = line.split()[1]
                        if state in fts3_active_list:   n_active   += 1
                        if state in fts3_failed_list:   n_failed   += 1
                        if state in fts3_finished_list: n_finished += 1
                        
                    if line.split()[0] == 'Reason:':
                        reason = ''.join(line)

                    ## Write failure log:
                    if state == 'Failed':
                        fail_file.write(rmNL(id)+': ' +reason     +'\n'  )
                        fail_file.write('source:     '+source     +'\n'  )
                        fail_file.write('destination:'+destination+'\n\n')

                            

            ## Print message
            message = '%4d active, %4d finished and %4d failed files in ' % (n_active,n_finished,n_failed)
            message += rmNL(id)
            print message
                      
            ## Remove complete failures from FTS queue
            if n_failed and not n_active:
                command= "glite-transfer-cancel -s $FTS_SERVICE "+rmNL(id)
                lines,errors = runLCG(command,is_pexpect=False)
                if errors: raise Exception("Couldn't cancel transfer")

                ## Remove job id from list, now written to failures
                id_list.remove(id)
                print rmNL(id)+" Failed and was cancelled\n"

        except:
            print "Unexpected error:", sys.exc_info()[0]
            print '\n'.join(errors)

    ## Write the ammended job id list (minus failures) to the transfer log 
    log_file = open(log_name,'w')
    log_file.writelines(id_list)
    log_file.close()
    fail_file.close()

    ## Close completion file and remove if empty
    comp_file.close()
    comp_file = open(comp_name,'r')
    completions = comp_file.readlines()
    comp_file.close()


    if not len(completions):
        if os.path.exists(comp_name):
            os.remove(comp_name)

        
    


    
