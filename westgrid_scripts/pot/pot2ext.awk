#!/bin/awk -f
{
    r=substr($0,15,4);s=substr($0,20,4);i=(r s);
    stat = system("fgrep -q '" r " " s "' spill-check/beam0runs.list")
    printf "%s %s %#9.5g %#9.5g %d\n", r,s,$2,$3,stat
}
