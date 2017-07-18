#!/usr/bin/env python

import sys
import os

print "Importing ROOT..."
from ROOT import *
gROOT.ProcessLine('.x ~/rootlogon.C')
gROOT.SetBatch(1)
print "ROOT imported!"


### list of nd280 file types - need to determine this from names really
### keep underscores just in case file hashes match the same pattern
fileTypes = ['_anal_',
             '_cali_',
             '_cata_',
             '_cnfg_',
             '_cstr_',
             '_elmc_',
             '_g4mc_',
             '_gnmc_',
             '_logf_',
             '_numc_',
             '_nucp_',
             '_reco_',
             '_unpk_',
             'tar.gz',
             'cfg.tar',
             '.txt']

toGB =  1.0/(1024*1024*1024)
toTB = toGB/1024


def main():

    ### open input file
    if len(sys.argv) == 2:
        inFileName = sys.argv[1]
    else:
        print 'Please specify input file!'
        print 'e.g. ./auditAnalysis spaceAudit.root'
        sys.exit(1)
    file = TFile.Open(inFileName)

    ### get the TTree
    tree = file.Get('fileTree')

    ### add type contributions and keep a running sum
    contribs = {}

    ### integrate size contributions from each file type
    for type in fileTypes:
        tree.Draw("Entry$>>hSize","abs(size)*(name.find(\""+type+"\")!=-1&&srms==\"srm-t2k.gridpp.rl.ac.uk\")")
        h = gDirectory.Get('hSize')

        if not h.GetEntries():
            continue

        # gPad.WaitPrimitive()
        gPad.Update()

        contribs[type.replace('_','')]= h.Integral()

    totalSize = sum(contribs.values())

    ### compare totals
    tree.Draw("Entry$>>hSize","abs(size)*(srms==\"srm-t2k.gridpp.rl.ac.uk\")")
    h = gDirectory.Get('hSize')

    print 'Integrated total = %d bytes (%d GB)' % (int(totalSize),   int(   totalSize*toGB))
    print '       Raw total = %d bytes (%d GB)' % (int(h.Integral()),int(h.Integral()*toGB))
    

    ### print contributions 
    for type,size in contribs.iteritems():
         print '%9d GB of %7s data (%4.1f%%)' % (int(size*toGB),type,size/totalSize*100)

    ### calculate space saving by scaling back to 10% of g4mc, elcm, cali
    toTruncate = 'g4mc','elmc','cali'
    truncatedSize  = totalSize - 0.9*(sum(contribs[t] for t in toTruncate if t in contribs.keys()))
    print 'truncatedSize = %5d GB (%4.1f%%)'   % (int(truncatedSize*toGB),truncatedSize/totalSize*100)
    print 'Space saved   = %5.1f TB (%4.1f%%)' % (totalSize*toTB - truncatedSize*toTB, 100-truncatedSize/totalSize*100)
    
    
if __name__ == '__main__':
    main()


# 22490 12215
