#!/usr/bin/env python
"""
Dump all the raw ND280 data files on an SRM

Example usage:
     $ ./DumpRawData.py gfe02.grid.hep.ph.ic.ac.uk

jonathan perkin 20110222
"""

import os
import sys
import optparse
from time import sleep
import ND280GRID

parser = optparse.OptionParser()
(options,args) = parser.parse_args()
if len(args) != 1:
    sys.exit('Please specify a storage element on which to dump the raw data e.g.:\n     $ ./DumpRawData.py gfe02.grid.hep.ph.ic.ac.uk')
else:
    SRM=args[0]

## The SRM root directory
srm_root = ND280GRID.GetTopLevelDir(SRM)

## The local FTS transfer directory
transfer_dir= os.getenv("ND280TRANSFERS")

## The current raw data folder - don't run jobs beyond this
current_raw = ND280GRID.GetCurrentRawDataFolder()

## The LFC raw data directories
raw_root = 'nd280/raw/ND280/ND280/'
lfc_root = '/grid/t2k.org/'
command  = 'lfc-ls ' + lfc_root + raw_root
lines,errors = ND280GRID.runLCG(command)

if errors:
    print '\n'.join(errors)
else:
    ## Remove newlines
    lines = [ND280GRID.rmNL(l) for l  in lines]
    
    ## Truncate early data directories and any beyond current
    directories = lines[4:lines.index(current_raw)+1]

    ## Prioritise recent data
    directories.reverse()
    
    for directory in directories:

        ## The data directory
        data_dir = directory
        lfc_dir  = 'lfn:' + lfc_root + raw_root + data_dir +'/'
        srm_dir  = srm_root + raw_root + data_dir + '/'

        ## stdout and stderr redirection
        std_out = transfer_dir + '/' + data_dir + '.dump.' + SRM + '.out'
        std_err = std_out.replace('.out','.err')
        
        ## Run SyncDirs.py
        command="./SyncDirs.py -a "+lfc_dir+" -b "+srm_dir+" -f 1 >"+std_out+" 2>"+std_err+" &"
        print command
        os.system(command)

        ## Wait a minute
        sleep(60)
