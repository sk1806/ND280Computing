#!/bin/bash

echo 'aghhhh' > file1.txt
ls 
echo $PWD
ls $PWD
pwd

## SE=se03.esc.qmul.ac.uk
## SE=SRM://se03.esc.qmul.ac.uk
## SE=DIRAC
## SE=DIRAC-USER
SE=UKI-LT2-QMUL2-disk

#FILE=./file.txt



FILE=file1.txt 
# this works when i run the job locally

#FILE=${PWD}/filei1.txt

LFN=/t2k.org/soph/file1.txt
dirac-dms-add-file ${LFN} ${FILE} ${SE}

