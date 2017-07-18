#!/bin/bash
#PBS -l nodes=1:ppn=8,walltime=24:00:00
#PBS -N cherryPick_ccpizero

air_water=water
sample=ccpizero   #ccpiplus(6) ccpizero(4) ncpiplus(5) ncpizero(3) nue (2)
i_sample=4    # 2-7
i_waterair=1  #1 
selection="leptons:1;pi0:1"         #"leptons:0;pi0:1"   #"leptons:1;pi+:1" "12,-12"
source /home/s/soser/tfeusels/setup_v11r21.sh
basedir=/home/s/soser/tfeusels/t2k_scratch/neut_production/production006/A/mcp/neut/2010-11-${air_water}/basket/${sample}/numc
#for i_run in `seq 0 19`
for i_run in `seq 0 23`
#for i_run in `seq 0 9`
#for i_run in `seq 0 161`
#for i_run in `seq 0 15`
#for i_run in `seq 0 3`
do
    run=${i_run}
    if [ ${i_run} -lt 10 ]
    then 
	run=00${i_run}
    elif [ ${i_run} -lt 100 ]
    then 
	run=0${i_run}
    fi
    #for i in `seq 0 39`
    #for i in `seq 0 55`
    for i in `seq 0 43`
    do
	curr_dir=${basedir}/902${i_waterair}${i_sample}${run}/${i}
	OLD_FILE=`ls ${curr_dir}/*c.root`
	NEW_FILE=`echo ${OLD_FILE/.root/_all.root}`
	echo $NEW_FILE
	mv ${OLD_FILE} ${NEW_FILE}
	CHERRYPICK.exe -c "${selection}" $NEW_FILE -o $OLD_FILE
	#CHERRYPICK.exe -n "${selection}" $NEW_FILE -o $OLD_FILE
	#fix filenames according to convention
	NEW_FILE=`echo ${OLD_FILE/beam/xxx}`
	#NEW_FILE=`echo ${OLD_FILE/beam/nue}`
	NEW_FILE=`echo ${NEW_FILE/prod6a/prod6}`
	NEW_FILE=`echo ${NEW_FILE/${air_water}c/${air_water}${sample}}`
	#NEW_FILE=`echo ${NEW_FILE/${air_water}c/${air_water}}`
	mv ${OLD_FILE} ${NEW_FILE}
	ls -lh ${curr_dir}/*.root
    done
done