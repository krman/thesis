#!/bin/bash

USAGE="usage: ./controller [start|stop] [objective]";

if [[ ( $1 == "stop" ) ]]; then
    pid=`ps aux | grep pox | grep log | cut -d " " -f 7 | head -1`
    kill -9 $pid 2>/dev/null
    sudo mn -c >/dev/null 2>/dev/null
fi
if [[ ( $1 == "start" ) ]]; then
    ../controllers/pox_base.sh --objective=$2
fi

exit 0;
