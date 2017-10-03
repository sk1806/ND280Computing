#!/usr/bin/env python

import optparse
import ND280GRID
#from ND280GRID import ND280JDL
#from ND280GRID import ND280JID
import ND280GRID_old
import os
import sys
import time
import pexpect
import commands


print(' ')
print('------------------------------- ')
print('    Testing ND280JID class    ')
print('------------------------------- ')

print(' ')
print(' ')
print('Testing members of ND280JID object:   ')
j1 = ND280GRID_old.ND280JID('ND280MC_spill_v12r9_80730298_0055.jid')

print(' ')
print('jidfilename:  '),
print(j1.jidfilename)
print('jobno:        '),
print(j1.jobno)
print('status:       '),
print(j1.status)
print('exitcode:     '),
print(j1.exitcode)
print('statusreason: '),
print(j1.statusreason)
print('dest:         '),
print(j1.dest)
print(' ')

print('ND280GRID_old.ND280JID.GetStatus(j1):'),
print( ND280GRID_old.ND280JID.GetStatus(j1) )

print('ND280GRID_old.ND280JID.GetExitCode(j1):'),
print( ND280GRID_old.ND280JID.GetExitCode(j1) )

print('ND280GRID_old.ND280JID.GetStatusReason(j1):'),
print( ND280GRID_old.ND280JID.GetStatusReason(j1) )

print('ND280GRID_old.ND280JID.GetRunNo(j1):'),
print( ND280GRID_old.ND280JID.GetRunNo(j1) )

print('ND280GRID_old.ND280JID.GetSubRunNo(j1):'),
print( ND280GRID_old.ND280JID.GetSubRunNo(j1) )

print('ND280GRID_old.ND280JID.GetOutput(j1):'),
print( ND280GRID_old.ND280JID.GetOutput(j1) )

print('ND280GRID_old.ND280JID.IsDone(j1):'),
print( ND280GRID_old.ND280JID.IsDone(j1) )

print('ND280GRID_old.ND280JID.IsRunning(j1):'),
print( ND280GRID_old.ND280JID.IsRunning(j1) )

print('ND280GRID_old.ND280JID.IsScheduled(j1):'),
print( ND280GRID_old.ND280JID.IsScheduled(j1) )

print('ND280GRID_old.ND280JID.IsExitClean(j1):'),
print( ND280GRID_old.ND280JID.IsExitClean(j1) )




print(' ')
print(' ')
print(' ')
print(' ')
# This is what glite gives you when you get the status of a list of JIDs
#$ glite-wms-job-status -i list.jid
#------------------------------------------------------------------
#1 : https://lcglb01.gridpp.rl.ac.uk:9000/o0wYVEq15Wnb6UXctKoxCA
#2 : https://lcglb02.gridpp.rl.ac.uk:9000/TJ4Vk_ZfNLrsZOKFk7l_ZQ
#a : all
#q : quit
#------------------------------------------------------------------

#j2 = ND280JID('glite_jid_list_2.jid')

print('Testing Jons thing on a list of 1 JID ')

command1 = "glite-wms-job-status -i glite_jid_list_1.jid"
child1 = pexpect.spawn(command1)
index1 = child1.expect(['list - \[([0-9]+)\-?([0-9]+)\]?all:', pexpect.EOF, pexpect.TIMEOUT])
# somehow through the magic of regex, this returns
# 1  if one file in list
# 0  if multiple files in list
print(index1)
print(' ')


print('Testing Jons thing on a list of 2 JID ')
command2 = "glite-wms-job-status -i glite_jid_list_2.jid"
child2 = pexpect.spawn(command2)
#print(child2)
index2 = child2.expect(['list - \[([0-9]+)\-?([0-9]+)\]?all:', pexpect.EOF, pexpect.TIMEOUT])
# somehow through the magic of regex, this returns
# 1  if one file in list
# 0  if multiple files in list
print(index2)
print(' ')
