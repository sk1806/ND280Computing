#!/bin/bash
for f in run?xxx_magoff_runs.list; do
  if [[ $f == "run3xxx_magoff_runs.list" ]]; then continue; fi
  c=${f/_magoff_/_cos_};
  r=${f:3:1}
  echo $f
  cat runs123/$c $f >| tmp.lis
  curl --data-binary @tmp.lis -k -H 'Accept: text/plain' -X POST "https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/A/rdp/ND280/0000${r}000_0000${r}999?COSMIC"
done