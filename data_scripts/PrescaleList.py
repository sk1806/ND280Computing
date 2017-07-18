#!/usr/bin/env python 

import optparse
import os
import sys
import time
import commands

#Parser options
parser = optparse.OptionParser()

#Mandatory
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to process")

#Optional
parser.add_option("-s","--prescale",dest="prescale",type="string",help="Submit every n:th file")


(options,args) = parser.parse_args()

###############################################################################

# Main Program

filename=options.filename
if not filename:
    sys.exit('Please give a filelist using the -f or --filelist flag')

if options.prescale:
    prescale = int(options.prescale)

listfile=open(filename,'r')
filelist=listfile.readlines()
listfile.close()

counter = 0
counter2 = 0
for f in filelist:
    counter += 1
    if counter%prescale > 0:
        continue
    else:
        counter2 += 1
        f=str(f.replace('\n',''))
        print f
    
print '--------------------------------'
print 'To be Submitted: ' + str(counter2) + ' jobs, with prescaling ' + str(prescale) 
print 'Original file had ' + str(counter) + ' files ' 
