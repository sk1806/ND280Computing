#!/usr/bin/env python
"""
Register Current Raw Data Files on T2 - to be ran 4 x daily by CRON
jonathan perkin 20110214
"""

import os
import sys
from ND280GRID import *


## The T2 SEs
SEs=['gfe02.grid.hep.ph.ic.ac.uk',
     'se03.esc.qmul.ac.uk',
     'ccsrm02.in2p3.fr',
     'hepgrid11.ph.liv.ac.uk',
     'lcgse0.shef.ac.uk',
     'srm.pic.es',
     't2se01.physics.ox.ac.uk',
     'fal-pygrid-30.lancs.ac.uk']

srmlist=''
for se in SEs: srmlist += se+' '

## The data folder 0000*000_0000*999
data_folder = GetCurrentRawDataFolder()

## The full LFC current raw data path
dir='/grid/t2k.org'+GetCurrentRawDataPath()+'/'

## The logging folder
transfer_dir= os.getenv("ND280TRANSFERS")

## stdout and stderr redirection
out_file=transfer_dir+'/'+data_folder+'.T2.reg.'+str(datetime.now().hour)+'.out'
err_file=out_file.replace('.out','.err')

## Run RegDarkData.py
command="./RegDarkData.py -l lfn:"+dir+" "+srmlist+" >"+out_file+" 2>"+err_file+" &"
print command
os.system(command)
