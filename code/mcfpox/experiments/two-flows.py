#!/usr/bin/python

from mcfpox.topos import pentagon
from mcfpox.objectives import shortest_path, max_spare_capacity, widest_path
from boilerplate import start, results

import matplotlib.pyplot as plt
from termcolor import colored


def experiment(bw, module):
    pairs = [('h1','h2'), ('h1','h2')]
    flows = {
        15: [(i,j,bw) for i,j in pairs]
    }

    scenario = {
        'net': pentagon,
        'flows': flows
    }

    controller = {
        'objective': module.objective,
    }

    return start(scenario, controller)


if __name__ == '__main__':
    bw = [0]
    sp = [0]
    msc = [0]
    wp = [0]

    for i in [3,5,7,9]:
        j = '{0}m'.format(i)
        bw.append(2*i)

        string = "\nTrial: shortest path, offered load {0} Mbps".format(2*i)
        print
        print colored(string, "blue", attrs=['bold'])
        recv = experiment(j, shortest_path)
        sp.append(sum(recv))

        string = "\nTrial: widest path, offered load {0} Mbps".format(2*i)
        print
        print colored(string, "yellow", attrs=['bold'])
        recv = experiment(j, widest_path)
        wp.append(sum(recv))

        string = "\nTrial: max spare capacity, offered load {0} Mbps".format(2*i)
        print
        print colored(string, "red", attrs=['bold'])
        recv = experiment(j, max_spare_capacity)
        msc.append(sum(recv))

    plt.figure()
    plt.plot(bw, [i/1e6 for i in sp], 'g-o',label='Shortest path')
    plt.plot(bw, [i/1e6 for i in wp], 'r-*',label='Widest path')
    plt.plot(bw, [i/1e6 for i in msc], 'b-x',label='Max spare capacity')
    plt.axis([0,25,0,25])
    plt.xlabel("Aggregate offered load (Mbps)")
    plt.ylabel("Aggregate throughput (Mbps)")
    plt.title("mcfpox demonstration")
    plt.legend()
    save = "demo.png"
    plt.savefig(save)
    plt.show()
