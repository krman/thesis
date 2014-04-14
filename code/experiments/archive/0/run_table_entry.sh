#!/bin/bash

function cleanup {
    echo "end of experiment, shutting down..." >&2
    echo "results saved in $temp_dir" >&2
    #kill $pid_tcpdump 2>/dev/null
    kill $pid_pox 2>/dev/null
    kill $pid_python 2>/dev/null
    echo "experiment complete."
}
trap cleanup EXIT

eid=0
etitle="ofp_flow_mod vs ofp_packet_out"
echo "starting experiment $eid: $etitle" >&2

src_dir=/home/imz/src
temp_dir=$src_dir/thesis/temp
pox_dir=$src_dir/pox

# start monitoring packets
#tcpdump -i any -w $temp_dir/packet.dump &
#pid_tcpdump=$!

for trial in flow-mod packet-out
do
    echo "test run: $trial"
    rm $temp_dir/controller-$trial.log $temp_dir/mininet-$trial.log

    for num in {1..5}
    do
	echo 
	$pox_dir/pox.py log.level --packet=WARN thesis.base-$trial 2>>$temp_dir/controller-$trial.log &
	pid_pox=$!

	python test_table_entry.py >>$temp_dir/mininet-$trial.log &
	pid_python=`jobs -l python | awk '{print $2}'`
	wait $pid_python
	kill $pid_pox
    done
done

# this jobs stuff is probably not necessary. i'm tired.
python process_table_entry.py $temp_dir > $temp_dir/results
pid_python=$!
wait $pid_python
