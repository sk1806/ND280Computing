#!/bin/bash

source $VO_T2K_ORG_SW_DIR/nd280v11r31/setup.sh

env

cat << EOF > test.C
{
  f = TFile::Open("test.root","RECREATE");
  h = new TH1F("h","h",100,-1,1);
  h->FillRandom("gaus");
  h->Fit("gaus");
  h->Write();
}
EOF

root -b -q test.C

if [ -e test.root ]; then 
    exit 0
fi

exit 1

