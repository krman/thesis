#!/bin/bash

USAGE="usage: ./controller [start|stop]";
[ $# -ne 1 ] && echo $USAGE && exit 1;

if [[ ( $1 == "stop" ) ]]; then
    pid=`ps aux | grep pox | grep log | cut -d " " -f 7 | head -1`
    kill -9 $pid
fi
if [[ ( $1 == "start" ) ]]; then
    cd ../controllers
    ./pox_base.sh
fi

exit 0;
