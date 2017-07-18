#!/usr/bin/env python

#---------------------------------------------------------------
#Script to modify t2k.org nd280 software tags
#Remember to change proxy to Role=lcgadmin
#---------------------------------------------------------------

import optparse
import ND280GRID
import os
import time
import pexpect
import commands

# Parser Options

parser = optparse.OptionParser()

#Mandatory settings
parser.add_option("-c","--ce",dest="ce",type="string",help="CE to install on, e.g. 0 for lcgce05.gridpp.rl.ac.uk, CE number, or all for all CEs")
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to install")
parser.add_option("-m","--modify",dest="modify",type="string",help="Set to 1 to add tag and -1 to remove tag")

(options,args) = parser.parse_args()

###############################################################################

# Main Program

nd280ver = options.version
if not nd280ver:
    sys.exit("Please specify a version to install using the -v or --version flag")

ce=options.ce
if not ce:
    sys.exit('Please enter the event type you wish to process using the -e or --evtype flag')

modify=options.modify
if not modify or abs(int(modify)) != 1:
    sys.exit('Please set -m to 1 or -1')
mod=int(modify)

site_list=['lcgce05.gridpp.rl.ac.uk',
                      'lcgce0.shef.ac.uk',
                      'hepgrid6.ph.liv.ac.uk',
                      'ceprod03.grid.hep.ph.ic.ac.uk',
                      'ce04.esc.qmul.ac.uk',
                      't2ce02.physics.ox.ac.uk',
                      'fal-pygrid-44.lancs.ac.uk',
                      'cccreamceli09.in2p3.fr',
                      'ce03.ific.uv.es',
                      'ce07.pic.es']


#0 RAL
#1 Sheffield
#2 Liverpool
#3 Imperial
#4 QMUL
#5 Oxford
#6 Lancaster
#7 in2p3
#8 IFIC
#9 PIC



#site_list=['lcgce05.gridpp.rl.ac.uk','lcgce0.shef.ac.uk','hepgrid5.ph.liv.ac.uk','ceprod03.grid.hep.ph.ic.ac.uk','ce03.esc.qmul.ac.uk','t2ce02.physics.ox.ac.uk','fal-pygrid-44.lancs.ac.uk','cclcgceli03.in2p3.fr','ce03.ific.uv.es','ce07.pic.es']

addremove=''
if mod == 1:
    addremove='add'
    print 'Adding tags'
elif mod == -1:
    addremove='remove'
    print 'Removing tags'

nsite=0
isite=-1
for site in site_list:
    isite += 1

    if ce.isdigit():
        if int(ce) != isite:
            continue
    else:
        if ce != 'all' and site != ce:
            continue

    print site

    command='lcg-tags -ce '+site+' --vo t2k.org --'+addremove+' --tags VO-t2k.org-ND280-'+nd280ver

    rtc=os.system(command)
    if rtc:
        print 'failed to run ' + command
    else:
        nsite += 1

        
print '--------------------------------'
print 'Changed ' + str(nsite) + ' tags'

