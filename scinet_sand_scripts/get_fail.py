#!/usr/bin/env python   
import os
import sys
import shutil
import commands

import subprocess

f = open('redo_newneut.txt')
lines = f.readlines()
f.close()

phrase = "["
nline = 0
for line in lines: 
    #print line
    file = line.strip("\n").split("/")[17]
    #print file
    runsub = file.split("_")[3]
    run = runsub.split("-")[0]
    subrun = runsub.split("-")[1]

    #print run + " " + subrun
    #print int(subrun)

    phrase += "[\"" + run + "\",\"" + str(int(subrun)) + "\"]"
    nline = nline + 1
    if nline < 8:
        phrase += ","
    else:
        phrase += "]"
        print phrase
        phrase = "["
        nline = 0
    
phrase += "]"
print phrase


