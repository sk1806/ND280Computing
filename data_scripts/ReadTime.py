#!/usr/bin/env python

#Script that gets the average processing time from log files

import os
import sys
import popen2
import optparse

# Parser Options
parser = optparse.OptionParser()

parser.add_option("-o","--outdir",dest="outdir",type="string",help="Output directory with log files")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

outdir=options.outdir
if not outdir:
    sys.exit('Please specify the outdir with -o')
    
command = 'ls '+outdir+'/*.log' 
o,i,e=popen2.popen3(command)
logs=o.readlines()

longt=36000
nruns=0
nlongruns=0
sumt=0
for l in logs:
    l=l.replace('\n','')
    lfile=open(l,'r')
    lines=lfile.readlines()

    line=lines[-1]

    tag='Total Processing Time: '
    s=' seconds'
    if tag in line:
        tline=line.replace(tag,'')
        t=float(tline.replace(s,''))
        print t
        nruns+=1
        sumt+=t
        if t > longt:
            nlongruns+=1

avt=sumt/nruns
avth=avt/3600
print '--------------------------------------------'
print '  Average processing time = '+str(avt)+' s'
print '  or '+str(avth)+' h'
print '  long runs (>10 h): '+str(nlongruns)+' out of: '+str(nruns)
