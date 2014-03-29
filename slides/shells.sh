#!/bin/sh

USAGE="usage: ./shells.sh [start|stop|restart]";
[ $# -ne 1 ] && echo $USAGE && exit 1;

if [[ ( $1 == "stop" ) || ( $1 == "restart" ) ]]; then
    pkill -f shellinaboxd
fi
if [[ ( $1 == "start" ) || ( $1 == "restart" ) ]]; then
    shellinaboxd -b -s /:imz:imz:HOME:SHELL --localhost-only --linkify=normal --css=white-on-black.css
fi

exit 0;
