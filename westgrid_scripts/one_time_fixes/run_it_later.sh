#!/bin/bash

while true; do
  if [[ -z $(qstat -u t2k) ]]; then break; fi
  echo "sleeping..."
  sleep 633
done

./gen_qsub.pl v10r11p27 nd280_rdp_spill_all.pbs SPILL production005/G/fpp/ND280 work/run123_spl_files.list wg-bugaboo
