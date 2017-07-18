#!/usr/bin/env python 

import optparse
from ND280GRID import ND280JID
import os
import smtplib

from email.MIMEText import MIMEText

# Parser Options

parser = optparse.OptionParser()
## Common with genie_setup
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to install")
#parser.add_option("-e","--evtype",     dest="evtype",     type="string",help="Event type, spill or cosmic trigger")
parser.add_option("-o","--outdir",     dest="outdir",     type="string",help="Output directory. Can also specify using $ND280JOBS env variable. Defaults to $PWD/Jobs if neither are present")
parser.add_option("-r","--runno",     dest="runno",     type="string",help="Run number, or start of - used for listing")
(options,args) = parser.parse_args()

###############################################################################

# Main Program

nd280ver = options.version
if not nd280ver:
    sys.exit("Please specify a version to install using the -v or --version flag")

runno=options.runno

##evtype=options.evtype
##if not evtype:
##    sys.exit('Please enter the event type you wish to process using the -e or --evtype flag')
	
outdir=options.outdir
if not outdir:
    outdir=os.getenv("ND280JOBS")
    if not outdir:
        outdir=os.getenv("PWD") + '/Jobs/'
outdir += '/' + nd280ver ## Always add nd280ver to path to keep separate.

print outdir

## Check the output directory exsits, if not then exit
if not os.path.isdir(outdir):
    sys.exit('The directory ' + outdir + ' does not exist.')

command = 'ls ' + outdir + '/' 
if runno:
    command += '*_' + runno + '*.jid'
else:
    command += '*.jid'
lines,errors = ND280GRID.runLCG(command,is_pexpect=False)

print lines
print errors

message_lines=[]

message_text='Dear Sir/Madam,\n\n'

sendmail=0

for l in lines:
    j=ND280JID(l.replace('\n',''))
    
    if j.IsDone():
        ## Get the output if done
        outputdir = j.GetOutput()
        if not j.IsExitClean():
            sendmail=1
            message_text+='Not a clean exit for ' + l
    elif 'Aborted' in j.status:
        message_text+='Job aborted ' + l
            

message_text+= '\nCheers,\n\nBen'

##Send the mail if there are errors to comment on
if sendmail==1:
    # Create a text/plain message
    print 'Errors present so sending mail'
    msg = MIMEText(message_text)
    
    me = 'b.still@qmul.ac.uk'
    you = 'b.still@qmul.ac.uk'
    msg['Subject'] = '***ND280 Processing ERROR***'
    msg['From'] = me
    msg['To'] = you
    
    s = smtplib.SMTP('mail.hep.ph.qmul.ac.uk')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

