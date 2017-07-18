#!/usr/bin/env python

"""
Python tool that creates a local nd280Version with a CMT install area and a location independent version of ROOT
and produces a tarball for deployment on CVMFS
"""


import optparse
import glob
import os
import re
import shutil
import stat
import sys
import tarfile

from ND280GRID import FindAndReplaceStringInFile
from distutils.version import LooseVersion


## default path in which to create binary distribution is /scratch/$USER/t2k
defaultOutputPath='/scratch/%s/t2k' %(os.getenv('USER'))


## parse the arguments and options
parser = optparse.OptionParser(usage="""usage: %prog [options] <nd280_version>""")
parser.add_option('--cleanUp',                    action='store_true',                           help='Delete the build (but not the tarball)'                                                  )
parser.add_option('--cmtpath',                    default='',                                    help='Override CMTPATH, i.e. the directory in outputPath that the build is contained in'       )
parser.add_option('--cvmfsLibs',                  default='lib-Linux2.6.32-431.23.3.el6.x86_64', help='The system libraries installed on CVMFS'                                                 )
parser.add_option('--cvmfsROOT',                  default='/cvmfs/t2k.egi.eu',                   help='The ubiquitous CVMFS root directory, under normal circumstances this = VO_T2K_ORG_SW_DIR')
parser.add_option('--inputFileList',              default='input-file.list',                     help='When building nd280AnalysisTools, the path to input-file.list must be specified'         )
parser.add_option('--module',                     default="nd280",                               help='The name of the module to build (default is nd280)'                                      )
parser.add_option('--moduleBroadcast',            action='store_true',                           help='Optionally issue a cmt broadcast in the module build'                                    )
parser.add_option('--moduleVersion',              default='',                                    help='Specify the version of the module to build, (it if isn\'t nd280). An even revision is assumed to be the head')
parser.add_option('--nd280AnalysisToolsVersion',  default='v1r9p3',                              help='When building nd280Highland2, a version of the nd280AnalysisTools is required'           )
parser.add_option('--noClean',                    action='store_true',                           help='Don\'t make clean'                                                                       )
parser.add_option('--noTar',                      action='store_true',                           help='Skip the tarball generation'                                                             )
parser.add_option('--outputPath',                 default=defaultOutputPath,                     help='Local path in which to create binary distribution'                                       )
parser.add_option('--recursive',                  action='store_true',                           help='Force a recursive CMT checkout'                                                          )
parser.add_option('-f',dest='forced',             action='store_true',                           help='Force fresh CMT checkout'                                                                )
(options,args)   = parser.parse_args()


## make sure a module version is specified if building a single module
if options.module != 'nd280' and not options.moduleVersion: 
    parser.print_help()
    sys.exit(1)


## check the validity of cvmfsROOT and cvmfsLibs
for p in options.cvmfsROOT, options.cvmfsROOT+'/'+options.cvmfsLibs:
    if not os.path.exists(p):
        print 'Path not found: %s' % (p)
        sys.exit(1)


## for now, only support builds of a full nd280Highland2 release (i.e. not individual modules)
if 'highland' in options.module.lower() and options.module != 'nd280Highland2':
    print 'Only builds of the full nd280Highland2 release are supported at present, sorry.'
    sys.exit(1)
                      

## installing nd280 software, so cvsroot now has to point to nd280 repo (not t2k)
os.environ['CVSROOT']=':ext:anoncvs@repo.nd280.org:/home/trt2kmgr/ND280Repository'

   

## method to determine if an os.walk-ed root and file are pertinient to the nd280 release
def IsPertinent(f='',root=''):

    if f.endswith('.d'       )  : return False
    if f.endswith('.gmk'     )  : return False
    if f.endswith('.last'    )  : return False
    if f.endswith('.o'       )  : return False
    if f.endswith('.rootcint')  : return False
    if f.endswith('stamp'    )  : return False

    if '.make'    in f.lower()  : return False
    if 'gnumake'  in f.lower()  : return False
    if 'makefile' in f.lower()  : return False
    if 'cmake'    in f.lower()  : return False
    if 'readme'   in f.lower()  : return False

    if 'CVS'          in root   : return False
    if '_deps'        in root   : return False
    if '/mysql-test/' in root   : return False
    if 'root/icons'   in root   : return False
    if 'root/docbook' in root   : return False
    if root.endswith('/doc')    : return False
    if root.endswith('/docs')   : return False

    return True


## method to write setup script used by ND280Job 
def WriteSetupScript(nd280ver='',tarballFolder=''):
    print 'Writing setup script...'
    
    scriptLines = [
    '#!/bin/bash',
    '',
    'if [ -z "$VO_T2K_ORG_SW_DIR" ]; then',
    '\techo \'$VO_T2K_ORG_SW_DIR is unset! Aborting\'',
    '\treturn 1',
    'fi',
    '',
    'if [ -z "$CMTROOT" ]; then',
    '\techo \'setting $CMTROOT to $VO_T2K_ORG_SW_DIR/CMT/v1r20p20081118\'',
    '\texport CMTROOT=$VO_T2K_ORG_SW_DIR/CMT/v1r20p20081118',
    'fi',
    '',
    'export LD_LIBRARY_PATH=$VO_T2K_ORG_SW_DIR/%s:$LD_LIBRARY_PATH' % (options.cvmfsLibs),
    'export CMTPATH=$VO_T2K_ORG_SW_DIR/nd280%s'                     % (nd280ver)
    ]

    if options.module == 'nd280':
        scriptLines += [
            'source $CMTPATH/nd280/%s/cmt/setup.sh'                 % (nd280ver)
            ]
    else:
        module  = options.module
        version = options.moduleVersion
        scriptLines += [
            'export CMTPATH=$VO_T2K_ORG_SW_DIR/%s:$CMTPATH'         % (module+version),
            'source $VO_T2K_ORG_SW_DIR/%s/%s/%s/cmt/setup.sh'       % (module+version,module,version)
            ]
    scriptLines += ['']

    ## write the setup script
    setupName = tarballFolder+'/setup.sh'
    setup     =  open(setupName,'w')
    setup.write('\n'.join(scriptLines))
    setup.close()

    ## set the permissions
    os.chmod(setupName,493)

    return


## method to form the binary distro tarball
def CompressTarball(tarballFolder='',outputPath=''):
    print 'Compressing tarball...'
    os.chdir(outputPath)

    outputBase = os.path.basename(tarballFolder)
    tarName    = outputBase
    if not os.uname()[2] in tarName:
        tarName += '-' + os.uname()[2] 
    tarName += '.tgz'

    tarBall    = tarfile.open(tarName,'w:gz')
    tarBall.add(outputBase)
    tarBall.close()
    print '%s is complete!' % (tarName)
    return


## method to replace symlinks in InstallArea and $ROOTSYS with cvmfs compliant ones
def ReplaceInstallAreaLinks(cmtpath='',outputPath=''):
    print 'Replacing InstallArea symlinks...'
    installArea = cmtpath + '/InstallArea/' + os.getenv('CMTCONFIG')

    for d in 'lib','bin':
        os.chdir(installArea+'/'+d)

        for link in [ l for l in os.listdir(os.getcwd()) if not l.endswith('.cmtref') ]:
            readlink = os.readlink(link)
            print 'Unlinking ' + readlink
            os.unlink(link)

            source = readlink.replace(outputPath,options.cvmfsROOT)
            print 'Linking ' + source + ' -> ' + link
            os.symlink(source,link)

            cmtref = open(link+'.cmtref','w')
            cmtref.write(source+'/n')
            cmtref.close()

    ## fix ROOSYS?
    rootsys = glob.glob('%s/ROOT/v*/%s' % (cmtpath,os.getenv('CMTCONFIG')))
    if not rootsys : return
    else           : print 'Replacing $ROOTSYS symlinks...'
       
    for d in 'lib','bin','include':
        link = rootsys[0] + '/' + d
        
        readlink = os.readlink(link)
        print 'Unlinking ' + readlink
        os.unlink(link)

        source = readlink.replace(outputPath,options.cvmfsROOT)
        print 'Linking ' + source + ' -> ' + link
        os.symlink(source,link)


def UpdateBuildStrategy(cmtpath=''):
    print 'Updating build strategy...'

    ## now update the build strategy for EXTERN and nd280Policy
    os.chdir(cmtpath)
    requirementsList = glob.glob('*/v*/cmt/requirements')

    if options.module == 'nd280':
        requirementsList = [ x for x in requirementsList if ('EXTERN' in x or 'nd280Policy' in x) ]
        for path in requirementsList:
            FindAndReplaceStringInFile(path,'without_install_area','with_installarea')
            FindAndReplaceStringInFile(path,'without_installarea', 'with_installarea') # sometimes it is mis-spelt

    if not options.module == 'nd280' and not 'highland' in options.module.lower(): 
        for path in requirementsList:
            ## use nd280Policy to build with installarea
            readlines   = open(path,'r').readlines()
            writelines  = []
            uselines    = [ l for l in readlines if l.startswith('use ') ]
            if not any(['nd280Policy' in l for l in uselines]):
                ## write at beginning of file if missing
                writelines.append('use nd280Policy *\n')
                for r in readlines:
                    writelines.append(r)
            ## only rewrite if necessary
            if writelines:
                open(path,'w').writelines(writelines)
        return

    ## fpr nd280, copy modified compile_root from cvmfs/nd280v11r31, later releases will have an up to date version
    ## check the versions first
    compileRootWrk = glob.glob('%s/ROOT/v*/src/compile_root' % (cmtpath))[0]
    wrkRootVer     = compileRootWrk.split('ROOT/v')[1].split('/')[0].split('n')[0]
    wrkRootVer     = re.sub('[a-z]', '.', wrkRootVer)

    
    ## return if current version is newer
    if LooseVersion(wrkRootVer) > LooseVersion('5.34.09'):
        print 'compile_root is up to date'
        return

    print 'Copying compile_root from cvmfs...'
    compileRootDev = options.cvmfsROOT+'/nd280v11r31/ROOT/v5r34p09n04/src/compile_root'
    shutil.copy(compileRootDev,compileRootWrk)

    
    ## find and replace root version 5.34.09 with correct one
    FindAndReplaceStringInFile(compileRootWrk,'VERSION=root_v5.34.09','VERSION=root_v%s' % (wrkRootVer))
    print open(compileRootWrk).read()  


## define the build command for an nd280 release and cd to the build directory
def ND280BuildCommand(cmtpath='',nd280ver=''):
    print 'Building location independent ND280'

    os.environ['VO_T2K_ORG_SW_DIR'] = options.outputPath # override default
    buildCommand = "source %s/nd280/%s/cmt/setup.sh\ncmt show uses\ncmt broadcast '" % (cmtpath,nd280ver)
    if not options.noClean: buildCommand += "cmt config; make clean; "
    buildCommand += "make VERBOSE=1;'"

    return buildCommand


## the build command for an nd280 module release
def ModuleBuildCommand(cmtpath='',nd280ver=''):
    print 'Building binary distribution of %s %s' % (options.module,options.moduleVersion)

    ## append CMTPATH with nd280 release aginst which this module is being built
    os.environ['CMTPATH'] =  os.getenv('CMTPATH') + ':' + os.getenv('VO_T2K_ORG_SW_DIR')+'/nd280'+nd280ver
    print 'CMTPATH = %s' % os.getenv('CMTPATH')

    buildCommand = 'source %s/setup.sh\n' % (os.getcwd())
    if     options.moduleBroadcast : buildCommand += 'cmt broadcast \'' 
    if not options.noClean         : buildCommand += 'cmt config; make clean && ' # assume configuration changes if making clean...
    if     options.moduleBroadcast : buildCommand += 'make\';'
    else                           : buildCommand += 'make;'

    return buildCommand


## the build command for an nd280Highland2 release
def HighlandBuildCommand(cmtpath='',nd280ver=''):
    print 'Building binary distribution of %s %s' % (options.module,options.moduleVersion)
    
    ## append CMTPATH with nd280 release aginst which this module is being built - required for compatible version of ROOT
    os.environ['CMTPATH'] =  os.getenv('CMTPATH') + ':' + os.getenv('VO_T2K_ORG_SW_DIR')+'/nd280'+nd280ver
    print 'CMTPATH = %s' % os.getenv('CMTPATH')
    
    ## first setup ROOT
    rootSetup = glob.glob('%s/nd280%s/ROOT/v*/cmt/setup.sh' % (os.getenv('VO_T2K_ORG_SW_DIR'),nd280ver))[0]
    buildCommand = 'source %s\n' % (rootSetup)

    buildCommand += "cmt broadcast '"
    if not options.noClean : buildCommand += 'make clean; '
    buildCommand += "make'"

    return buildCommand


## CMT checkout the software
def GetTheSoftware(cmtpath=''):
    print 'Getting the software...'
    
    os.chdir(cmtpath)
    command  = 'pwd\necho $CVSROOT\ncmt co '

    ## recursive checkout for nd280 and highland
    if options.module == 'nd280' or options.module == 'nd280Highland2' or options.recursive:
        command += ' -R ' 
        
    command += options.module
    ## if the moduleVersion is even, assume we're getting the head and don't specify the revision
    if int(''.join([s for s in list(options.moduleVersion) if s.isdigit()]))%2 : 
        command += ' -r ' + options.moduleVersion
    print command; rtc = os.system(command)
    if rtc: 
        print 'CMT checkout failed'
        sys.exit(1)
        

    ## if this is a highland build, get nd280AnalysisTools too
    if options.module == 'nd280Highland2':
        command = 'pwd\necho $CVSROOT\ncmt co nd280AnalysisTools -r %s ' % (options.nd280AnalysisToolsVersion)
        print command; rtc = os.system(command)
        if rtc : 
            print 'CMT checkout of nd280AnalysisTools %s failed' % (options.nd280AnalysisToolsVersion)
            sys.exit(1)

        ## also need to specify input-file.list, overwrite the original with the file specified by options.inputFileList
        original = '%s/nd280AnalysisTools/%s/AnalysisTools/input-file.list' % (cmtpath,options.nd280AnalysisToolsVersion)
        print 'Overwriting %s with %s' % (original,options.inputFileList)
        shutil.copy(options.inputFileList,original)


## Fix permissions (some of the GEANT dat files are always wrong and this breaks the cvmfs synchonisation)
def FixPermissions(cmtpath=''):
    print 'Fixing permissions in %s' % (cmtpath)

    os.chdir(cmtpath)

    # not very pythonic
    command = 'find %s -type f -exec chmod go+r {} \;'  % cmtpath
    print command
    os.system(command)

    command = 'find %s -type d -exec chmod go+rx {} \;' % cmtpath
    print command
    os.system(command)


## main program
def main():

    ## was the nd280 version specified?
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    nd280ver = args[0]
    for v in nd280ver, options.moduleVersion:
        if not v.startswith('v'): v = 'v' + nd280ver


    ## override moduleVersion for nd280
    if options.module == 'nd280' : options.moduleVersion = nd280ver


    ## does the output path exist?
    if not os.path.exists(options.outputPath):
        if os.makedirs(options.outputPath):
            print 'Unable to create output path %s, aborting!' % (options.outputPath)
            sys.exit(1)
    os.chdir(options.outputPath)

    
    ## make (a new) <module>v*r* folder to contain this build and export it to CMTPATH
    if options.cmtpath : cmtpath = options.cmtpath
    else               : cmtpath = '%s/%s%s' % (options.outputPath,options.module,options.moduleVersion) 

    if os.path.exists(cmtpath):
        if options.forced:
            print 'Deleting existing %s' % (cmtpath)
            shutil.rmtree(cmtpath)

    if not os.path.exists(cmtpath):
        os.makedirs(cmtpath)
    os.environ['CMTPATH'] = cmtpath


    ## get the software
    GetTheSoftware(cmtpath)


    ## update the build strategy
    UpdateBuildStrategy(cmtpath)


    ## cd to the build directory and define the cmt build command
    os.chdir('%s/%s/%s/cmt' % (cmtpath,options.module,options.moduleVersion)) 
    if   options.module == 'nd280'         : buildCommand =    ND280BuildCommand(cmtpath,nd280ver)
    elif options.module == 'nd280Highland2': buildCommand = HighlandBuildCommand(cmtpath,nd280ver)
    else                                   : buildCommand =   ModuleBuildCommand(cmtpath,nd280ver)
        

    ## run the build...
    print 'os.getcwd():%s'  % (os.getcwd())
    print 'buildCommand:%s' % (buildCommand)
    rtc = os.system(buildCommand)    
    if rtc : print buildCommand + " failed"; os.system('env'); sys.exit(1) 


    ## remove non-pertinent files
    for root, dirs, files in os.walk(cmtpath,followlinks=True):
        for f in files:
            p  = root + '/' + f
            if not IsPertinent(f,root):
                print 'Removing %s' % (p)
                os.remove(p)


    ## fix permissions, 
    FixPermissions(cmtpath)


    ## write the setup script executed by ND280Job
    WriteSetupScript(nd280ver,cmtpath)


    ## replace symlinks in InstallArea (and $ROOTSYS)
    ReplaceInstallAreaLinks(cmtpath,options.outputPath)
    
    
    ## REPAIR gsl-config??


    ## create the tarball
    if not options.noTar:
        CompressTarball(cmtpath,options.outputPath)


    ## clean up?
    if options.cleanUp:
        shutil.rmtree(cmtpath)
        

    ## end of program
    print '%s %s has been packaged for deployment.' % (options.module,options.moduleVersion)
    if options.module == 'nd280':
        print 'Please remember to run nd280-get-beam and nd280-get-geometry on remote server.'
        print 'Please check $ROOTSYS/bin and $ROOTSYS/lib links exist and are correct on remote server'
    sys.exit(0)


if __name__ == '__main__':
    main()
