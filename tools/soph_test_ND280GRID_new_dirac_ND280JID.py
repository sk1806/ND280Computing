#!/usr/bin/env python

import optparse
import ND280GRID
#from ND280GRID import ND280JDL
#from ND280GRID import ND280JID
import ND280GRID
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
print('File containing one JID   ')
j1 = ND280GRID.ND280JID('diracONEjobs_spill_v12r9_00000000_0001.jid')

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

print('ND280GRID.ND280JID.GetStatus(j1):'),
print( ND280GRID.ND280JID.GetStatus(j1) )

print('ND280GRID.ND280JID.GetExitCode(j1):'),
print( ND280GRID.ND280JID.GetExitCode(j1) )

print('ND280GRID.ND280JID.GetStatusReason(j1):'),
print( ND280GRID.ND280JID.GetStatusReason(j1) )

print('ND280GRID.ND280JID.GetRunNo(j1):'),
print( ND280GRID.ND280JID.GetRunNo(j1) )

print('ND280GRID.ND280JID.GetSubRunNo(j1):'),
print( ND280GRID.ND280JID.GetSubRunNo(j1) )

print('ND280GRID.ND280JID.GetOutput(j1):'),
print( ND280GRID.ND280JID.GetOutput(j1) )

print('ND280GRID.ND280JID.IsDone(j1):'),
print( ND280GRID.ND280JID.IsDone(j1) )

print('ND280GRID.ND280JID.IsRunning(j1):'),
print( ND280GRID.ND280JID.IsRunning(j1) )

print('ND280GRID.ND280JID.IsScheduled(j1):'),
print( ND280GRID.ND280JID.IsScheduled(j1) )

print('ND280GRID.ND280JID.IsExitClean(j1):'),
print( ND280GRID.ND280JID.IsExitClean(j1) )








print(' ')
print(' ')
print(' ')
print(' ')
print('File containing two JIDs   ')
j2 = ND280GRID.ND280JID('diracTWOjobs_spill_v12r9_00000000_0002.jid')

print(' ')
print('jidfilename:  '),
print(j2.jidfilename)
print('jobno:        '),
print(j2.jobno)
print('status:       '),
print(j2.status)
print('exitcode:     '),
print(j2.exitcode)
print('statusreason: '),
print(j2.statusreason)
print('dest:         '),
print(j2.dest)
print(' ')

print('ND280GRID.ND280JID.GetStatus(j2):'),
print( ND280GRID.ND280JID.GetStatus(j2) )

print('ND280GRID.ND280JID.GetExitCode(j2):'),
print( ND280GRID.ND280JID.GetExitCode(j2) )

print('ND280GRID.ND280JID.GetStatusReason(j2):'),
print( ND280GRID.ND280JID.GetStatusReason(j2) )

print('ND280GRID.ND280JID.GetRunNo(j2):'),
print( ND280GRID.ND280JID.GetRunNo(j2) )

print('ND280GRID.ND280JID.GetSubRunNo(j2):'),
print( ND280GRID.ND280JID.GetSubRunNo(j2) )

print('ND280GRID.ND280JID.GetOutput(j2):'),
print( ND280GRID.ND280JID.GetOutput(j2) )

print('ND280GRID.ND280JID.IsDone(j2):'),
print( ND280GRID.ND280JID.IsDone(j2) )

print('ND280GRID.ND280JID.IsRunning(j2):'),
print( ND280GRID.ND280JID.IsRunning(j2) )

print('ND280GRID.ND280JID.IsScheduled(j2):'),
print( ND280GRID.ND280JID.IsScheduled(j2) )

print('ND280GRID.ND280JID.IsExitClean(j2):'),
print( ND280GRID.ND280JID.IsExitClean(j2) )
