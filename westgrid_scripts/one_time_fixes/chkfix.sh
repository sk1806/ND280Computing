#!/bin/bash
export SCRIPT_DIR=.

sr=000$2
sr=${sr: -4}
rr=${1:0:1}
#./check_mon_info.pl wg-bugaboo SPILL /global/scratch/t2k/production006/A/fpp/verify/v11r21/ND280/00009000_00009999/logf/oa_nd_spl_0000${1}-${sr}_*_logf_000_*-wg-bugaboo.log production006/A/fpp/verify/v11r21/ND280/00009000_00009999
#./check_mon_info.pl wg-bugaboo SPILL /global/scratch/t2k/production006/A/fpp/verify/v11r21/ND280/00009000_00009999/errors/oa_nd_spl_0000${1}-${sr}_*_logf_000_*-wg-bugaboo.log production006/A/fpp/verify/v11r21/ND280/00009000_00009999
./check_mon_info.pl wg-bugaboo SPILL /global/scratch/t2k/production006/I/rdp/ND280/0000${rr}000_0000${rr}999/logf/oa_nd_spl_0000${1}-${sr}_*_logf_000_*-wg-bugaboo.log production006/I/rdp/ND280/0000${rr}000_0000${rr}999                    
#./check_mon_info.pl wg-bugaboo COSMIC /global/scratch/t2k/production006/E/pc1/ND280/000${rr}000_000${rr}999/logf/oa_nd_cos_000${1}-${sr}_*_logf_000_*-wg-bugaboo.log production006/E/pc1/ND280/000${rr}000_000${rr}999                    
