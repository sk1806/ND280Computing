#!/usr/bin/env python

"""
A set of tools to install packages required by GENIE.

"""

import sys
import re
import tempfile
import os
import optparse
import shutil
import pexpect

##############################################################################
def install_genie(instDir="", version="", bashscr="", overwrite=True, make_include="", user_options=""):

    if not instDir:
        sys.exit("Please provide a directory in which to install GENIE")
    if not version:
        sys.exit("Please procide a version of GENIE to install, E.g. 2.6.4")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    genieDir = instDir+"Genie-"+version

    # Check the install directory.
    if not os.path.isdir(instDir):
       try:
          os.makedirs(instDir)
       except:
          sys.exit("Could not make installation directory")

    # Write setup script
    try:
       batchFH = open(bashscr,"a")
       batchFH.write("export GENIE=" + genieDir + "/\n")
       batchFH.write("export LD_LIBRARY_PATH=" + genieDir + "/lib/:$LD_LIBRARY_PATH\n")
       batchFH.write("export PATH=" + genieDir + "/bin/:$PATH\n")
       batchFH.close()
    except:
       sys.exit("Could not append bash setup script")

    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(genieDir):
            return genieDir

    # Remove any previous installations
    if os.path.isdir(genieDir):
        command="rm -rf " + genieDir
        rtc = os.system(command)
        if rtc:
            print "Could not remove " + command
    
    # First Get the source code
    os.chdir(instDir)
    command="wget http://www.hepforge.org/archive/genie/Genie-" + version + ".tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # untar
    os.chdir(instDir)
    command="tar -xzvf Genie-" + version + ".tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # If you want to replace the make_include
    if make_include:
        command = "cp " + make_include + " " + genieDir + "/src/make/Make.include"
        rtc = os.system(command)
        if rtc:
            sys.exit("Could not " + command)

    # source the setup script (need to do some acrobatics, since os.system("source setup.sh") doesn't work)
    try:
        batchFH = open(bashscr,"r")
        for l in batchFH:
            if "#!/bin/sh" in l:
                continue
            if "LD_LIBRARY_PATH" in l:
                suffix = os.getenv("LD_LIBRARY_PATH")
                l = l[0:-17]
            elif "PATH" in l:
                suffix = os.getenv("PATH")
                l = l[0:-6]
            else:
                suffix = ''
            splitl = l.split()
            splite = splitl[1].split('=')
            os.environ[splite[0]] = (splite[1]+suffix)
            print "Setting enviroment variable " + splite[0] + " to " + os.getenv(splite[0])
        batchFH.close()
    except:
        sys.exit("Could not decode the setup.sh file")
    #print some variables to show that its worked
    command="echo $PATH"
    print command
    os.system(command)
    command="echo $LD_LIBRARY_PATH"
    print command
    os.system(command)
    command="echo $GENIE"
    print command
    os.system(command)

    #Configure GENIE
    os.chdir(genieDir)
    command  = "./configure --disable-profiler --disable-validation-tools --disable-neut-cascade --disable-cernlib"
    command += " --disable-doxygen --disable-test --disable-viewer --disable-numi --disable-gsl --disable-debug"
    command += " --enable-mueloss --enable-atmo --enable-event-server" #can probably disable these 3
    command += " --enable-t2k --enable-flux-drivers --enable-geom-drivers --enable-rwght --enable-dylibversion"
    command += " --enable-lhapdf --with-lhapdf-lib=$LHAPDF_LIB --with-lhapdf-inc=$LHAPDF_INC"
    command += " --with-libxml2-lib=$LIBXML2_LIB --with-libxml2-inc=$LIBXML2_INC"
    command += " --with-log4cpp-lib=$LOG4CPP_LIB --with-log4cpp-inc=$LOG4CPP_INC"
    command += " --with-pythia6-lib=$PYTHIA6 --with-optmiz-level=O2"
    print command
    rtc = os.system(command)
    if rtc:
        sys.exit("Could not " + command)

    # Now Compile
    rtc = os.system("make")
    if rtc:
        os.system("echo $PATH")
        os.system("echo $LD_LIBRARY_PATH")
        sys.exit( "Failed to make GENIE" )

    #Overwrite UserPhysicsOption.xml -> enable charm decays
    command = "cp " + user_options + " " + genieDir + "/config/UserPhysicsOptions.xml"
    rtc = os.system(command)
    if rtc:
        sys.exit("Could not " + command)

    #Check its installed correctly
    if not os.path.isfile(genieDir+"/bin/gT2Kevgen"):
        sys.exit("gT2Kevgen executable not found. GENIE has not installed correctly")

    #Download the precomputed freenucleon splines
    os.chdir(instDir)
    #need to skirt around the fact that versions 2.6.4 and 2.6.6 are NOT physics upgrades -> use 2.6.2 splines
    if version == "2.6.4" or version == "2.6.6" or version == "2.6.8":
        version = "2.6.2"
    command = "wget http://www.hepforge.org/archive/genie/data/" + version + "/gxspl-freenuc-v" + version + ".xml.gz"
    rtc = os.system(command)
    if rtc and version != "2.8.0":
        sys.exit("Could not " + command)
        
    return genieDir

##############################################################################
def install_root(instDir="", version="", bashscr="", overwrite=True, pythia_path=""):

    if not instDir:
        sys.exit("Please provide a directory in which to install ROOT")
    if not version:
        sys.exit("Please procide a version of ROOT to install, E.g. 5.26.00")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    rootDir = instDir+"/root-"+version+"/root/"

    # Check the install directory.
    if not os.path.isdir(instDir):
       try:
          os.makedirs(instDir)
       except:
          sys.exit("Could not make installation directory")

    # Write setup script
    try:
        batchFH = open(bashscr,"a")
        batchFH.write("export ROOTSYS=" + rootDir + "\n")
        batchFH.write("export PATH=" + rootDir + "/bin/:$PATH\n")
        batchFH.write("export LD_LIBRARY_PATH=" + rootDir + "/lib/:$LD_LIBRARY_PATH\n")
        batchFH.close()
    except:
        sys.exit("Could not append bash setup script")

    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(rootDir):
            return rootDir
    # Remove any previous installations
    if os.path.isdir(rootDir):
        command="rm -rf " + rootDir
        rtc = os.system(command)
        if rtc:
            print "Could not remove " + command
          
    #Get the source
    if not os.path.isdir(instDir+"/root-"+version):
       try:
          os.makedirs(instDir+"/root-"+version)
       except:
          sys.exit("Could not make installation directory " + instDir+"/root-"+version)
    os.chdir(instDir+"/root-"+version)
    command="wget ftp://root.cern.ch/root/root_v" + version + ".source.tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # untar
    os.chdir(instDir+"/root-"+version)
    command="tar -xzvf root_v" + version + ".source.tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    #Configure ROOT
    os.chdir(rootDir)
    command="./configure --enable-pythia6 --with-pythia6-libdir=" + pythia_path + " --enable-builtin-freetype --disable-pythia8 --disable-fftw3"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit( "Failed to configure " + instDir )

    # Now Compile ROOT
    os.chdir(rootDir)
    command="make"
    rtc = os.system(command)
    if rtc:
        sys.exit( "Failed to make ROOT" )

    #Check its installed correctly
    if not os.path.isfile(rootDir+"/bin/root"):
        sys.exit("root executable not found. ROOT has not installed correctly")
        
    return rootDir

##############################################################################
def install_pythia6(instDir="", version="", bashscr="", overwrite=True):

    if not instDir:
        sys.exit("Please provide a directory in which to install Pythia6")
    if not version:
        sys.exit("Please procide a version of Pythia6 to install, E.g. 4_406")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    pythiaDir = instDir +"pythia6/"

    # Check the install directory.
    if not os.path.isdir(instDir):
        try:
            os.makedirs(instDir)
        except:
            sys.exit("Could not make installation directory " + instDir)

    # Write setup script
    try:
       batchFH = open(bashscr,"a")
       batchFH.write("export PYTHIA6=" + pythiaDir + "v" + version + "/lib/\n")
       batchFH.write("export LD_LIBRARY_PATH=" + pythiaDir + "v" + version + "/lib:$LD_LIBRARY_PATH\n")
       batchFH.close()
    except:
        sys.exit("Could not append bash setup script")

    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(pythiaDir):
            return pythiaDir
        
    # Remove any previous installations
    if os.path.isdir(pythiaDir):
        command="rm -rf " + pythiaDir
        rtc = os.system(command)
        if rtc:
            print "Could not remove " + command

    #Get the installation script
    if not os.path.isdir(pythiaDir):
        try:
            os.makedirs(pythiaDir)
        except:
            sys.exit("Could not make installation directory " + pythiaDir)
    os.chdir(pythiaDir)
    command="wget http://svn.hepforge.org/genie/branches/R-2_6_0/src/scripts/build/ext/build_pythia6.sh"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # Run the script
    os.chdir(pythiaDir)
    command="chmod +x build_pythia6.sh\n./build_pythia6.sh " + version
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    #Check its installed
    if os.path.isfile(pythiaDir + "v" + version + "/lib/libPythia6.so"):
        return  pythiaDir + "v" + version + "/"

    #If not installed correctly, try again with another option
    os.chdir(pythiaDir)
    command="chmod +x build_pythia6.sh\n./build_pythia6.sh " + version + " --dummies=keep"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)
       
    #Check its installed correctly
    if os.path.isfile(pythiaDir + "v" + version + "/lib/libPythia6.so"):
        return  pythiaDir + "v" + version + "/"
    sys.exit("libPythia6.so not found. Pythia6 has not installed correctly")

##############################################################################
def install_log4cpp(instDir="", version="", bashscr="", overwrite=True):

    if not instDir:
        sys.exit("Please provide a directory in which to install log4cpp")
    if not version:
        sys.exit("Please procide a version of GENIE to install, E.g. 1.1")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    log4cppDir = instDir +"log4cpp"

    # Check the install directory.
    if not os.path.isdir(instDir):
        try:
            os.makedirs(instDir)
        except:
            sys.exit("Could not make installation directory " + instDir)

    # Write setup script
    try:
       batchFH = open(bashscr,"a")
       batchFH.write("export LOG4CPP_INC=" + log4cppDir + "/install/include/\n")
       batchFH.write("export LOG4CPP_LIB=" + log4cppDir + "/install/lib/\n")
       batchFH.write("export LD_LIBRARY_PATH=" + log4cppDir + "/install/lib:$LD_LIBRARY_PATH\n")
       batchFH.close()
    except:
       sys.exit("Could not append bash setup script")

    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(log4cppDir):
            return log4cppDir
        
    # Remove any previous installations
    if os.path.isdir(log4cppDir):
        command="rm -rf " + log4cppDir
        rtc = os.system(command)
        if rtc:
            print "Could not remove " + command

    #Get the source code
    os.chdir(instDir)
    command="wget http://downloads.sourceforge.net/project/log4cpp/log4cpp-1.1.x%20%28new%29/log4cpp-1.1/log4cpp-1.1.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Flog4cpp%2Ffiles%2Flog4cpp-1.1.x%2520%2528new%2529%2Flog4cpp-1.1%2F"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # untar
    os.chdir(instDir)
    command="tar -xzvf log4cpp-1.1.tar.gz"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # Configure
    os.chdir(log4cppDir)
    command = "./configure --prefix=" + log4cppDir + "/install"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)
       
    # Compile
    os.chdir(log4cppDir)
    command="make"
    rtc = os.system(command)
    if rtc:
       sys.exit( "Failed to make log4cpp" )

    # Install
    os.chdir(log4cppDir)
    command="make install"
    rtc = os.system(command)
    if rtc:
        sys.exit( "Failed to make install log4cpp" )

    return log4cppDir


##############################################################################
def install_lhapdf(instDir="", version="", bashscr="", overwrite=True):

    if not instDir:
        sys.exit("Please provide a directory in which to install lhapdf")
    if not version:
        sys.exit("Please procide a version of lhapdf to install, E.g. 5.8.3")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    lhapdfDir = instDir + "lhapdf-" + version + "/"

    # Check the install directory.
    if not os.path.isdir(instDir):
       try:
          os.makedirs(instDir)
       except:
          sys.exit("Could not make installation directory " + instDir)

    # Write setup script
    try:
       batchFH = open(bashscr,"a")
       batchFH.write("export LHAPDF_LIB=" + lhapdfDir + "/install/lib/\n")
       batchFH.write("export LHAPDF_INC=" + lhapdfDir + "/install/include/\n")
       batchFH.write("export LHAPATH=" + lhapdfDir + "/install/bin/\n")
       batchFH.write("export LD_LIBRARY_PATH=" + lhapdfDir + "/install/lib:$LD_LIBRARY_PATH\n")
       batchFH.close()
    except:
       sys.exit("Could not append bash setup script")

    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(lhapdfDir):
            return lhapdfDir
        
    #Check for previous installs and remove
    if os.path.isdir(lhapdfDir):
        command = "rm -rf " + lhapdfDir
        rtc = os.system(command)
        if rtc:
            sys.exit("Could not " + command)
    
    # First Get the source code
    os.chdir(instDir)
    command="wget http://www.hepforge.org/archive/lhapdf/lhapdf-" + version + ".tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # untar
    os.chdir(instDir)
    command="tar -xzvf lhapdf-" + version + ".tar.gz lhapdf-" + version
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # Configure
    os.chdir(lhapdfDir)
    command = "./configure --prefix=" + lhapdfDir + "/install --enable-pdfsets=grv"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # Compile
    os.chdir(lhapdfDir)
    command="make"
    rtc = os.system(command)
    if rtc:
       sys.exit( "Failed to make lhapdf" )

    # Install
    os.chdir(lhapdfDir)
    command="make install"
    rtc = os.system(command)
    if rtc:
        sys.exit( "Failed to make install lhapdf" )

    # Download the PDFs
    os.chdir(lhapdfDir+"/install/bin")
    command = "./lhapdf-getdata GRV"
    rtc = os.system(command)
    if rtc:
        sys.exit( "Failed to download PDF libraries for lhapdf" )
        
    return lhapdfDir 


##############################################################################
def install_libxml2(instDir="", version="", bashscr="", overwrite=True):
    if not instDir:
        sys.exit("Please provide a directory in which to install libxml2")
    if not version:
        sys.exit("Please procide a version of libxml2 to install, E.g. 2.7.8")
    if not bashscr:
        bashscr = instDir+"/setup.sh" # Default

    libxml2Dir = instDir + "libxml2-" + version + "/"

    # Check the install directory.
    if not os.path.isdir(instDir):
       try:
          os.makedirs(instDir)
       except:
          sys.exit("Could not make installation directory " + instDir)

    # Write setup script
    try:
       batchFH = open(bashscr,"a")
       batchFH.write("export LIBXML2_LIB=" + libxml2Dir + "/install/lib/\n")
       batchFH.write("export LIBXML2_INC=" + libxml2Dir + "/install/include/libxml2\n")
       batchFH.write("export LD_LIBRARY_PATH=" + libxml2Dir + "/install/lib:$LD_LIBRARY_PATH\n")
       batchFH.close()
    except:
       sys.exit("Could not append bash setup script")
       
    # Exit if already installed (and don't want to overwrite)
    if not overwrite:
        if os.path.isdir(libxml2Dir):
            return libxml2Dir
    #Check for previous installs and remove
    if os.path.isdir(libxml2Dir):
        command = "rm -rf " + libxml2Dir
        rtc = os.system(command)
        if rtc:
            sys.exit("Could not " + command)

    # First Get the source code
    os.chdir(instDir)
    command="wget ftp://xmlsoft.org/libxml2/libxml2-" + version + ".tar.gz"
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)
         
    # untar
    os.chdir(instDir)
    command="tar -xzvf libxml2-" + version + ".tar.gz libxml2-" + version
    print command
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)

    # Configure
    os.chdir(libxml2Dir)
    command = "./configure --prefix=" + libxml2Dir + "/install"
    rtc = os.system(command)
    if rtc:
       sys.exit("Could not " + command)
       
    # Compile
    os.chdir(libxml2Dir)
    command="make"
    rtc = os.system(command)
    if rtc:
       sys.exit( "Failed to make libxml2" )

    # Install
    os.chdir(libxml2Dir)
    command="make install"
    rtc = os.system(command)
    if rtc:
        sys.exit( "Failed to make install libxml2" )

    return libxml2Dir
