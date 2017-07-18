#!/usr/bin/env python 

import optparse
import os
from ND280Job import ND280Raw
from ND280GRID import ND280File

# Parser Options

parser = optparse.OptionParser()
## Common with genie_setup
parser.add_option("-d","--destination",dest="destination",type="string",help="Destination for data")
parser.add_option("-i","--input",      dest="input",      type="string",help="Input to process, must be an lfn")
parser.add_option("-v","--version",    dest="version",    type="string",help="Version of nd280 software to install")
parser.add_option("-e","--evtype",     dest="evtype",     type="string",help="Event type, spill or cosmic trigger")

(options,args) = parser.parse_args()

###############################################################################

# Main Program 
##srm://srm-t2k.gridpp.rl.ac.uk/castor/ads.rl.ac.uk/prod
destination=options.destination
if not destination:
    sys.exit('Please enter a destination for the output')

nd280ver=options.version
if not nd280ver:
    sys.exit('Please enter a version of the ND280 Software to use')

## example input is 'lfn:/grid/t2k.org/nd280/raw/ND280/ND280/00005000_00005999/nd280_00005216_0000.daq.mid.gz'
input=options.input
if not input and not 'lfn:' in input:
    sys.exit('Please enter an lfn: input file')

evtype=options.evtype
if not evtype:
    sys.exit('Please enter the event type you wish to process using the -e or --evtype flag')

os.system('env')


input_file=ND280File(input)
    
## Create Job object
j=ND280Raw(nd280ver,'/data/wilson/T2K/T2KComputingRep/CERNBeamProcessing/Testing/',input_file,evtype)

## Run the Job
j.SetQuick()
j.Run()


## Build up the path srm://srm-t2k.gridpp.rl.ac.uk/castor/ads.rl.ac.uk/prod/t2k.org/nd280/v7r19p1/logf/ND280/ND280/00003000_00003999/
path_prot=destination + '/t2k.org/nd280/' + nd280ver + '/'
reg_path_prot='lfn:/grid/t2k.org/nd280/' + nd280ver + '/'
path_end='CERNTestBeam/' + input_file.GetRunRange() + '/'

## Tar and copy the catalogue files
j.CopyCatalogueFiles(path_prot + 'cata/' + path_end)

## Copy across the root files, register some
copyfiles=['ectb','cali','erec','anal','logf']
registerfiles=['cali','anal','erec']
#registerfiles=[]

j.CopyRootFiles(path_prot,path_end,copyfiles,registerfiles, reg_path_prot, path_end)
