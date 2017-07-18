#!/usr/bin/python

# Wrapper script for RunND280Process.py that submits neutSetup jobs across runs and subruns for TChained flux files
# N.B. for /cvmfs flux inputs, NFLUX=1

# Original implementation split flux files into 18x60 hadded files, found here /grid/t2k.org/beam/mc/beamMC/flux13a/hadd/
# such that neutSetup.RHC.list would have the following contents:
#
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.000_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.001_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.002_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.003_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.004_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.005_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.006_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.007_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.008_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.009_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.010_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.011_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.012_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.013_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.014_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.015_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.016_fix.root
# lfn:/grid/t2k.org/beam/mc/beamMC/flux13a/hadd/fluka_13a_nom_nd6_m250ka.60x.017_fix.root
#

# Now that all the flux events reside in a single hadded file on cvmfs, the contents of neutSetup.RHC.list are:
#
# /cvmfs/t2k.egi.eu/flux/nu.13a_nom_ND6_m250ka_flukain.all.root
#

# Don't forget the 'm'inus in the horn current for FHC and RHC input paths respectively, e.g.: *_250ka*.root and  *_m250ka*.root

import os
import sys
from ND280GRID import *
from glob import glob

# job submission PARAMETERS
ISTEST    = False                                                             # need to invoke RunND280Process test mode to regenerate missing JDL for individual job resubmissions
RUN       = 0                                                                 # run number to start on
FILELIST  = os.getenv('ND280JOBS')+'/lists/neutSetup.RHC.list'                # the file containing list of flux file LFNs
LISTLINES = [ l.strip() for l in open(FILELIST).readlines() ]                 # the file list lines
NFLUX     = len(LISTLINES)                                                    # the number of flux files in the list - the total no. of subruns is a multiple of this number
OFFSET    = 0                                                                 # a subrun offset is applied once NFLUX subruns have been submitted
RUNMAX    = 5                                                                 # the maximum run number to submit
SUBCYCLES = 56                                                                # the number of times to cycle through NFLUX subruns
SUBMAX    = SUBCYCLES*NFLUX                                                   # the total number of subruns to submit SUBCYCLES*NFLUX

# The usual arguments to RunND280Process.py                                   # Run numbering system: ZABCDEEE
ND280VER  = 'v11r31p11'                                                       # Z : 9 -> Neutrino MC, 8 -> Anti-neutrino MC
PROD      = '6L'                                                              # A = Generator (0: NEUT, 1: GENIE, 2: old NEUT)
RUNCODE   = '80620'                                                           # B = ND280 Data Run (with a certain beam condition and set of dead channels assumed for each run)
NEUTVER   = '5.3.2'                                                           # C = 0: P0D air, 1: P0D water
POT       = '5E17'                                                            # D = Volume / Sample type (0: Magnet, 1: Basket (beam), 2: nue, 3: NC1pi0, 4: CC1pi0, 5: NC1pi+, 6: CC1pi+, 7: tpcgas)
GENERATOR = 'anti-neut'                                                       # E = MC Run number
GEOMETRY  = '2015-08-air'
VERTEX    = 'magnet'
BEAM      = 'run6'

# optionally submit to a resource...
RESOURCE  =''                                                                 # RESOURCE  = 'lcgce1.shef.ac.uk:8443/cream-pbs-t2k'

# -- end of job submission PARAMETERS --

# limit on the number of parallel processes (LFC I/O)
nProcMax=10

# loop over runs
while RUN < RUNMAX:

    # loop over subruns
    while OFFSET < SUBMAX:

        # submit NFLUX jobs via the RunND280Process.py
        command  = './RunND280Process.py -e spill -f %s -j MC -v %s -p %s -t mcp ' % (FILELIST,ND280VER,PROD)
        command += '-c runCode=%s%03d,subrunOffset=%d --neutVersion=%s --POT=%s '  % (RUNCODE,RUN,OFFSET,NEUTVER,POT)
        command += '-g %s -a %s -y %s -w %s'                                       % (GENERATOR,GEOMETRY,VERTEX,BEAM)

        # test mode writes JDL but does not submit
        if ISTEST:
            command += ' --test'

        # optionally submit to a specific resource (not in test mode)
        if not ISTEST and RESOURCE :
            command += ' -r '+ RESOURCE

        print command
        lines,errors = runLCG(command,is_pexpect=False)  # - multiple sub-processes desireable here using ND280GRID.processWait()

        # increment the subrun offset
        OFFSET += NFLUX

    # reset the subrun offset after SUBCYCLES*NFLUX subruns
    OFFSET = 0

    # increment the run number
    RUN += 1

sys.exit()

