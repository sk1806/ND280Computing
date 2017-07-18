#!/usr/bin/env python

"""
Wrapper script for GenerateSpaceAudit.py that launches it on
the subdirectories of the specified input path

N.B. presently there is no support for the GenerateSpaceAudit.py
options apart from the requisite --lfcDir

e.g. for input path /grid/t2k.org/nd280/production004, one instance
of the script is launched for each of the subdirectories
$ lfc-ls /grid/t2k.org/nd280/production004
A
B
C
D
E
F
Z

if the pattern option is used, then only the directories matching the
pattern are audited

e.g. for input path /grid/t2k.org/nd280 with --pattern nd280/v
v10r11p3
v10r11p9
v10r9p1
v7r19
v7r19p1
v7r19p3
v7r19p7
v7r19p9
v7r21p5
v8r5
v8r5p1
v8r5p11
v8r5p13
v8r5p3
v8r5p7
v8r5p9
v9r11p1
v9r7p11
v9r7p3
v9r7p5
v9r7p9
v9r9p1
"""

from ND280GRID import runLCG
import optparse
import os
import sys

# option parser
usage     = "usage: %prog [options] lfcpath"
parser    = optparse.OptionParser(usage=usage)
parser.add_option("--pattern", default='',   help="only audit directories matching <pattern>")
parser.add_option("--stdNull", default=False,help="set to True if stdout/stderr redirection to /dev/null is desired") 
(options,args) = parser.parse_args()

# balk if no LFC path
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

lfcPath = sys.argv[1]

# list contents of LFC path
command = "lfc-ls "+lfcPath
lines,errors = runLCG(command,is_pexpect=False)

# parse pattern option
if options.pattern:
    directories = [lfcPath+'/'+line for line in lines if options.pattern in lfcPath+'/'+line]
else:
    directories = [lfcPath+'/'+line for line in lines]

for dir in directories:
    # output redirection
    if not options.stdNull:
        stdOut = os.getenv("ND280SCRATCH")+'/audit.'+'.'.join(dir.split('/')[-2:])+'.out'
        stdErr = stdOut.replace('.out','.err')
    else:
        stdOut = '/dev/null'
        stdErr = stdOut
        
    command = "nohup nice ./GenerateSpaceAudit.py --lfcDir="+dir+" >"+stdOut+" 2>"+stdErr+" &"
    print command
    os.system(command)



