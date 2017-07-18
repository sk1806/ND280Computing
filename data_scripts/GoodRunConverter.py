#Script to change lists into useful lists

import optparse
import sys

parser = optparse.OptionParser()
parser.add_option("-f","--filename",dest="filename",type="string",help="File containing filenames to process")
parser.add_option("-o","--outname",dest="outname",type="string",help="Output file name")
(options,args) = parser.parse_args()

filename=options.filename
if not filename:
    sys.exit('Please give a filelist using the -f or --filelist flag')

outname=options.outname
if not outname:
    sys.exit('Please specify output file name with -o')

listfile=open(filename,'r')
filelist=listfile.readlines()
listfile.close()

outfile=open(outname,'w')

lfnbase='lfn:/grid/t2k.org/nd280/raw/ND280/ND280/'
filebase='nd280_0000'
fileend='.daq.mid.gz'

for i,f in enumerate(filelist):

    if i < 3:
        continue

    thisline=f.split()
    run=str(thisline[0])
    subrun=str(thisline[1])

    setnr=str(run[0])
    set='0000'+setnr+'000_0000'+setnr+'999/'

    if len(subrun) == 3:
        subrun = '0'+subrun
    elif len(subrun) == 2:
        subrun = '00'+subrun
    elif len(subrun) == 1:
        subrun = '000'+subrun
    else:
        sys.exit('Bad length: '+str(f))
    filename=lfnbase+set+filebase+run+'_'+subrun+fileend
    outfile.write(filename+'\n')

outfile.close()
i-=3
print 'Wrote '+str(i)+' runs to '+outname
