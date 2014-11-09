"""
Experiment framework module: boilerplate code for network experiments
"""

import re
import os
import sys
import json
import time
import sched
import subprocess
from multiprocessing import Process
from termcolor import colored

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController


def start_log(log_dir):
    """
    Initialise logging directory with either suggested name or timestamped name.
    """
    if not log_dir:
        log_dir = 'log.{0}'.format(int(time.time()))
    subprocess.call(['mkdir', '-p', log_dir])
    return {'log_dir': log_dir}
    

def start_net(net, logs):
    """
    Start a previously-created network. Logging is currently disabled.
    """
    print "Starting mininet: no logs"
    net.start()
    return net


def start_pox(logs, level={}, module='mcfpox.controller.base',
              objective=None, rules=None, poxdesk=False):
    """
    Launch the POX controller.
    Note: relies on the github.com/krman fork of POX.
    """
    
    log_level = {
        'INFO': True,
        'packet': 'WARN',
    }
    log_level.update(level)
    
    logs['pox'] = 'pox.log'
    print "Starting POX: log files in {0}".format(logs['pox'])

    args = {
        module: [{
            'objective': objective
        }],
        'log.level': [log_level]
    }   

    if poxdesk:
        args.update({
            #'samples.pretty_log': [{}],
            'web': [{}],
            'messenger': [{}],
            'messenger.log_service': [{}],
            'messenger.ajax_transport': [{}],
            'openflow.of_service': [{}],
            'poxdesk': [{}],
            'poxdesk.tinytopo': [{}],
        })
    
    def start(components):
        from pox.boot import boot
        out_log = os.path.join(logs['log_dir'], 'pox.out')
        err_log = os.path.join(logs['log_dir'], 'pox.err')
        #sys.stdout = open(out_log, 'w')
        sys.stderr = open(err_log, 'w')
        boot({'components':components})
    
    process = Process(target=start, args=(args,))
    process.start()

    return process
    

def start_iperf(src, dst, port, bw, server_log, client_log):
    """
    Start iperf with given parameters and log both server and client.
    """
    server_cmd = "iperf3 -s -p {0} &> {1} &".format(
            port, server_log)

    blbw = str(int(bw[:-1]) * 1000.0/1070) + 'm'
    client_cmd = "iperf3 -c {0} -p {1} -b {2} -t 10 -O 10 -J &> {3}&".format(
            dst.IP(), port, blbw, client_log)

    print "Flow: {0} from {1} ({2}) to {3} ({4})".format(
            bw, src, src.IP(), dst, dst.IP())

    dst.cmd(server_cmd)
    src.cmd(client_cmd)


def start_flows(flow_schedule, net, logs):
    """
    Schedule iperf flows in network net according to given flow schedule.
    """
    s = sched.scheduler(time.time, time.sleep)
    port = 5101
    flow_logs = []
    log_dir = logs['log_dir']

    longest_delay = 0
    for delay, flows in flow_schedule.iteritems():
        for flow in flows:
            src = net.get(flow[0])
            dst = net.get(flow[1])
            bw = flow[2] 
            
            server_log = 'server.{0}.{1}'.format(dst, port)
            client_log = 'client.{0}.server.{1}.{2}'.format(src, dst, port)
            flow_logs.append((server_log, client_log))
            
            s.enter(delay, 1, start_iperf, (src, dst, port, bw, 
                    os.path.join(log_dir, server_log), 
                    os.path.join(log_dir, client_log),))
            port += 1
        longest_delay = max(longest_delay, delay)

    logs['flows'] = flow_logs
    time.sleep(1)

    print "\nStarting scheduled flows: iperf output in server/client logs"
    s.run()
    print

    time.sleep(longest_delay+15)
                  
                  
def start(scenario, config, log_dir=None):
    """
    Start POX and Mininet with the given configuration.
    """
    logs = start_log(log_dir)
    print "Starting experiment: log files in {0}".format(logs['log_dir'])

    try:
        net = start_net(scenario['net'].create_net(), logs)
        controller = start_pox(logs, **config)
        
        start_flows(scenario['flows'], net, logs)
        
        net.stop()
        controller.terminate()

    except KeyboardInterrupt as e:
        print "Exiting on user command"
        raise
    finally:
        print colored("End of experiment:", "green", attrs=['bold']),

    return results(scenario, config, logs)


def results(scenario, config, logs):
    """
    Process iperf results and write summary to file.
    Return measured throughput array for all flows.
    """
    log_dir = logs['log_dir']
    recv = []

    src_pattern = re.compile("client.(h[0-9]+).server.(h[0-9]+).([0-9]+)")

    print
    
    for slog, clog in logs['flows']:
        server_log = os.path.join(log_dir, slog)
        client_log = os.path.join(log_dir, clog)

        src_host, dst_host, dst_port = src_pattern.match(clog).groups()
        
        with open(client_log, 'r') as f:
            try:
                j = json.load(f)
                r = j['end']['sum_received']['bits_per_second']
                recv.append(r)
            except (ValueError, KeyError):
                r = 0.0
                recv.append(0)
        
        string = "{0} - {1}:{2}: {3} bps".format(src_host, dst_host, dst_port, r)
        print colored(string, "green")
    
    pox_log = os.path.join(log_dir, "pox.err")
    process = subprocess.Popen(["grep", "Rules", pox_log],
                    stdout=subprocess.PIPE)
    output, err = process.communicate()

    process.wait()
    rules = output.split("Rules are ")[-1]

    scenario["net"] = scenario["net"].__name__
    config["objective"] = config["objective"].__module__

    summary = {
        "scenario": scenario,
        "config": config,
        "results": recv,
        "rules": rules,
        "logs": log_dir
    }

    string = "Total throughput {0} Mbps".format(sum(recv)/1e6)
    print colored(string, "green", attrs=['bold'])

    with open("results.json", 'a') as f:
        f.write(json.dumps(summary, sort_keys=True, 
                indent=4, separators=(',', ': ')))
        f.write("\n")
    
    return recv
