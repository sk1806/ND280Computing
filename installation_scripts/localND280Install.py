#!/usr/bin/env python

import sys
import re
import tempfile
import os
import optparse
import shutil
import stat
import glob

from ND280Software import ND280Software

""" A standard style install. """

##############################################################################
# Parser Options

parser = optparse.OptionParser()
parser.add_option("-v","--version",dest="version",type="string",help="Version of nd280 software to install")
parser.add_option("-d","--t2ksoftdir",dest="t2ksoftdir",type="string",help="Optional to pass the t2ksoftdir as an option, otherwise it must be set as an environment variable VO_T2K_ORG_SW_DIR")

(options,args) = parser.parse_args()
##############################################################################

# Get Options
nd280ver = options.version
if not nd280ver:
    raise Error("Please specify a version to install using the -v or --version flag")

sw = ND280Software(nd280ver)
sw.InstallCMT()
sw.GetND280()

## Make ND280 Software
sw.MakeND280()

## Get The beam data
sw.RunGetBeam()





