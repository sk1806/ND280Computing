#!/bin/awk -f
{printf "nd280_%08d_%04d.daq.mid.gz\n",$1,$2}
