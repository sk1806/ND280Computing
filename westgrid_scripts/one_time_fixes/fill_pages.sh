#!/bin/bash

trig=cos

if [[ $trig == cos ]]; then
    curl --data-binary @work/runs123/run4xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00004000_00004999?COSMIC'
    curl --data-binary @work/runs123/run5xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00005000_00005999?COSMIC'
    curl --data-binary @work/runs123/run6xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00006000_00006999?COSMIC'
    curl --data-binary @work/runs123/run7xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00007000_00007999?COSMIC'
    curl --data-binary @work/run8xxx_cos_runs_all.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00008000_00008999?COSMIC'
    curl --data-binary @work/run9xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00009000_00009999?COSMIC'

   exit 0
fi

if [[ $trig == spl ]]; then
#curl --data-binary @run9xxx_cos_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production005/F/fpp/ND280/00009000_00009999?COSMIC'
curl --data-binary @work/runs123/run4xxx_spl_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00004000_00004999?SPILL'
curl --data-binary @work/runs123/run5xxx_spl_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00005000_00005999?SPILL'
curl --data-binary @work/runs123/run6xxx_spl_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00006000_00006999?SPILL'
curl --data-binary @work/runs123/run7xxx_spl_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00007000_00007999?SPILL'
curl --data-binary @work/run8xxx_spl_runs_all.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00008000_00008999?SPILL'
curl --data-binary @work/run9xxx_spl_runs.list -k -H 'Accept: text/plain' -X POST 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/production006/B/rdp/ND280/00009000_00009999?SPILL'
exit 0

fi