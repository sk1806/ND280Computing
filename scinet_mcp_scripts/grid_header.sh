#!/bin/bash 
#
#############################################################################
#
# Title: SciNet GRID transfer header
#
# Usage: This contains a function that sets the storage element (SE) and 
#        proper remote root directory you wish to copy to. The actual sample
#        directory must be specified in the calling script as well as the 
#        desired site, via the variable SITE which, for MC files, can be 
#        any of the following: ral, triumf or qmul3. There are also site
#        specific flags defined (only TRIUMF for now).
#                 
#
#############################################################################

# This is the Logical File Catalogue (LFC) root directory 
LFN="grid/t2k.org/nd280"


# Define SEs, their root directories and any site specific flags here
function set_se {
    if [ "$SITE" == "ral" ]; then
	SE="srm-t2k.gridpp.rl.ac.uk"
	REMOTE_DIR="castor/ads.rl.ac.uk/prod/t2k.org/nd280"

    elif [ "$SITE" == "triumf" ]; then
	SE="t2ksrm.nd280.org"
	REMOTE_DIR="nd280data"
	
    elif [ "$SITE" == "qmul3" ]; then
	SE="se03.esc.qmul.ac.uk"
	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "shef" ]; then
#	SE="lcgse0.shef.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "liv" ]; then
#	SE="hepgrid11.ph.liv.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "ox" ]; then
#	SE="t2se01.physics.ox.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "in2p3" ]; then
#        SE="ccsrm02.in2p3.fr"
#        REMOTE_DIR="pnfs/in2p3.fr/data/t2k/t2k.org/nd280"

#    elif [ "$SITE" == "qmul1" ]; then
#	SE="se01.esc.qmul.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "ic" ]; then
#	SE="gfe02.grid.hep.ph.ic.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

#    elif [ "$SITE" == "man" ]; then
#	SE="bohr3226.tier2.hep.manchester.ac.uk"
#	REMOTE_DIR="t2k.org/nd280"

    else 
	echo "Unknown SITE: " $SITE
	exit 1
    fi

    # Special flag for copying to TRIUMF SRM
    if [ "$SITE" == "triumf" ]; then
	export GLOBUS_FTP_CLIENT_GRIDFTP2=true 
    else
	export GLOBUS_FTP_CLIENT_GRIDFTP2=false 
    fi

}
