#!/usr/bin/env python

"""
A script to install ROOT for GENIE.
Usage takes the form:
./installGENIE.py --inst_dir /data/t2k/dealtry/GENIE_install_scripts -m /data/t2k/dealtry/GENIE_install_scripts/Make.include --version-genie 2.6.4 --version-libxml2 2.7.8 --version-lhapdf 5.8.6 --version-pythia6 6_425 --version-root 5.30.02

./installGENIE.py --inst_dir /data/t2k/dealtry/GENIE_install_scripts -m /data/t2k/dealtry/GENIE_install_scripts/Make.include --version-genie 2.6.2 --version-libxml2 2.7.8 --version-lhapdf 5.8.6 --version-pythia6 6_425 --version-root 5.26.00
"""

import sys
import re
import tempfile
import os
import optparse
import shutil
import pexpect
import GENIE_Inst_Tools

##############################################################################
# Parser Options

parser = optparse.OptionParser()
parser.add_option("-g","--version-genie",dest="version_genie",type="string",help="Version of GENIE to install")
parser.add_option("-l","--version-lhapdf",dest="version_lhapdf",type="string",help="Version of LHAPDF to install")
parser.add_option("-p","--version-pythia6",dest="version_pythia6",type="string",help="Version of PYTHIA6 to install")
parser.add_option("-r","--version-root",dest="version_root",type="string",help="Version of ROOT to install")
parser.add_option("-x","--version-libxml2",dest="version_libxml2",type="string",help="Version of LIBXML2 to install")
parser.add_option("-m","--make_include",dest="make_include",type="string",help="Make.include for the GENIE install. Specify the full path, or it will be assumed that the file is in the current working directory")
parser.add_option("-u","--user_options",dest="user_options",type="string",help="UserPhysicsOptions.xml for the GENIE install -  will enable charm decay. Specify the full path, or it will be assumed that the file is in the current working directory")
parser.add_option("-d","--inst_dir",dest="inst_dir",type="string",help="Installation directory. If not set, defaults to enviroment variable VO_T2K_ORG_SW_DIR or VO_T2K_SW_DIR")
parser.add_option("-o","--overwrite",dest="overwrite",action="store_true",help="If set, will delete inst_dir/GENIE before starting installation process",default=False)
(options,args) = parser.parse_args()

###############################################################################

# Main Program

"""Obtain GENIE and 3rd party soft from http and install it."""


#find the t2k installation directory
inst_dir = options.inst_dir
if inst_dir:
   t2ksoftdir = inst_dir
else:
   t2ksoftdir = os.getenv("VO_T2K_ORG_SW_DIR")
if not t2ksoftdir:
   t2ksoftdir = os.getenv("VO_T2K_SW_DIR")
if not t2ksoftdir:
   optparse.OptionParser.print_help(parser)
   sys.exit("Could not get installation directory. Please use --inst_dir or set enviroment variable VO_T2K_ORG_SW_DIR")

#get the user input version numbers
version_libxml2 = options.version_libxml2
if not version_libxml2:
   optparse.OptionParser.print_help(parser)
   sys.exit('No libxml2 version specified. Please use --version-libxml2. It should be in the form "2.7.8" For a list of possible versions, please see:\nhttp://www.xmlsoft.org/news.html')

version_lhapdf = options.version_lhapdf
if not version_lhapdf:
   optparse.OptionParser.print_help(parser)
   sys.exit('No lhapdf version specified. Please use --version-lhapdf. It should be in the form "5.8.6" For a list of possible versions, please see:\nhttp://projects.hepforge.org/lhapdf/')

version_pythia6 = options.version_pythia6
if not version_pythia6:
   optparse.OptionParser.print_help(parser)
   sys.exit('No pythia6 version specified. Please use --version-pythia6. It should be in the form "6_425" For a list of possible versions, please see:\nhttp://www.hepforge.org/archive/pythia6/')

version_root = options.version_root
if not version_root:
   optparse.OptionParser.print_help(parser)
   sys.exit('No root version specified. Please use --version-root. It should be in the form "5.30.02" For a list of possible versions, please do:\nsvn ls http://root.cern.ch/svn/root/tags. Actually downloaded from ftp://root.cern.ch/root/ in file root_v<version>.source.tar.gz')

version_genie = options.version_genie
if not version_genie:
   optparse.OptionParser.print_help(parser)
   sys.exit('No genie version specified. Please use --version-genie. It should be in the form "2.6.2" For a list of possible versions, please do:\nsvn list https://svn.hepforge.org/genie/branches/, and check that the stable version you want is in tar format at http://www.hepforge.org/downloads/genie. If it is not, please email a reminder to thomas.dealtry@physics.ox.ac.uk')


#print out some enviroment information
command="echo $PATH"
print command
os.system(command)

base = os.getenv("PWD")
os.environ["BASE"]=base

#os.system("env")
#os.system("ls -lhRt " + t2ksoftdir)

#the make.include file to overwrite the default GENIE one
make_include=options.make_include

#the UserPhysicsOptions.xml file to overwrite the default GENIE one - to enable charm decay
user_options=options.user_options

if not "/" == make_include[0]:
   temp = make_include.rsplit('/')[-1]
   make_include = base + "/" + temp
   print "Using make include file:", make_include

if not "/" == user_options[0]:
   temp = user_options.rsplit('/')[-1]
   user_options = base + "/" + temp
   print "Using user options file:", user_options

# Check the install directory.
instDir = t2ksoftdir+"/GENIE/"

overwrite = options.overwrite
if overwrite:
   #make sure the installation directory is empty
   if os.path.isdir(instDir):
      command="rm -rf " + instDir
      rtc = os.system(command)
      if rtc:
         print "Could not remove " + command
print "Going to install GENIE and relevant 3rd party software in:\n" + instDir
if not os.path.isdir(instDir):
   try:
      os.makedirs(instDir)
   except:
      sys.exit("Could not make installation directory")

# Write setup script
bashscr = instDir+"/setup.sh"
try:
   batchFH = open(bashscr,"w")
   batchFH.write("#!/bin/sh\n")
   batchFH.close()
except:
   sys.exit("Could not write bash setup script")

print "instDir", instDir
print "bashscr", bashscr

# Install the 3rd party software
pythia_path  = GENIE_Inst_Tools.install_pythia6(instDir, version_pythia6, bashscr, True)
libxml2_path = GENIE_Inst_Tools.install_libxml2(instDir, version_libxml2, bashscr, True)
log4cpp_path = GENIE_Inst_Tools.install_log4cpp(instDir, "dummy",         bashscr, True)
lhapdf_path  = GENIE_Inst_Tools.install_lhapdf (instDir, version_lhapdf,  bashscr, True)
root_path    = GENIE_Inst_Tools.install_root   (instDir, version_root,    bashscr, True, pythia_path + "lib/")

## Now install GENIE
genie_path   = GENIE_Inst_Tools.install_genie  (instDir, version_genie,   bashscr, True, make_include, user_options)
print "Genie " + version_genie + " is installed at " + instDir

#find the computing element you're on
contact=os.getenv('GLOBUS_GRAM_MYJOB_CONTACT')
if not contact:
   sys.exit("Could not get GLOBUS_GRAM_MYJOB_CONTACT environment variable to determine CE")
ce=contact.split('/')[2].split(':')[0]

#And put the tag on the installation
os.chdir(instDir)
tag = "VO-t2k.org-GENIE-" + version_genie
command='lcg-tags --ce ' + ce + ' --vo t2k.org --add --tags ' + tag
rtc=os.system(command)
if rtc:
   sys.exit("Could not " + command)
