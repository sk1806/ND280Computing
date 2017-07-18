#!/usr/bin/env python

"""

Clear an srm raw data directory of its data and remove corresponding
entries from the LFC

jonathan perkin 20110309

"""

from ND280GRID import ND280File, ND280Dir, runLCG, rmNL
import optparse
import sys


# Parser Options
parser = optparse.OptionParser()
parser.add_option("-l","--lfcdir",dest="lfcdir",type="string",help="lfc directory to remove data from")
parser.add_option("-s","--srmopt",dest="srmopt",type="string",help="srm to remove data from")
(options,args) = parser.parse_args()

lfc_dir_name = options.lfcdir
srm_opt      = options.srmopt

# Parse LFC directory name
if not lfc_dir_name or not 'lfn:/' in lfc_dir_name or not srm_opt:
    parser.print_help()
    sys.exit(1)
    
# Create the N280Dir object
LFCDir = ND280Dir(lfc_dir_name,ls_timeout=3600)

# Keep list of files that are not at RAL - don't delete!
missingFromRAL = []

for LFCFile in  LFCDir.ND280Files:
    replicas = LFCFile.reps

    ## First ensure file is at RAL
    isAtRAL = False
    for rep in replicas:
        if 'srm-t2k.gridpp' in rep:

            ## make sure it isn't a null size replica:
            command = 'lcg-ls -l ' + rep
            lines,errors = runLCG(command)

            if lines and not errors:
                surl_size = int(lines[0].split()[-3])

                if surl_size == 0:
                    command = 'lcg-del ' + rep
                    lines,errors = runLCG(command)
                else:
                    isAtRAL = True
    if not isAtRAL:
        missingFromRAL.append(LFCFile.alias)
    else:
        for rep in replicas:
            if srm_opt in rep:
                
                # Use guid to remove file
                command = "lcg-del --vo t2k.org --verbose --se "+srm_opt+" "+LFCFile.guid
                lines,errors = runLCG(command)
                if errors:
                    print '\n'.join(errors)

if not len(missingFromRAL):
    print "All "+lfc_dir_name+" data deleted from "+srm_opt
else:
    for missing in missingFromRAL:
        print missing+" not replicated at RAL!"

