#!/usr/bin/python


import sys
import os
import re


if __name__ == '__main__':

    topo = sys.argv[1]

    sp = []
    wp = []
    msc = []
    
    pattern = re.compile(r'.*(h[0-9]+) - (h[0-9]+):[0-9]+: ([0-9]+)*')
    for trial in range(1,11):
        for bw in range(1,11):
            ext = "{0}.{1}".format(trial, bw)
            filename = "{0}.{1}".format(topo, ext)
            if not os.path.exists(filename): continue
            with open(filename, 'r') as f:
                for line in f:
                    if "shortest path" in line:
                        use = sp
                    elif "widest path" in line:
                        use = wp
                    elif "max spare capacity" in line:
                        use = msc

                    if " bps" in line:
                        match = pattern.match(line)
                        src,dst,recv = match.groups()
                        use.append((ext,src,dst,bw*1e6,recv))

    with open("extracted_results.csv", 'w') as f:
        f.write("\nshortest path\n")
        for data in sp:
            f.write("{0},{1},{2},{3},,{4}\n".format(*data))
        f.write("\nwidest path\n")
        for data in sp:
            f.write("{0},{1},{2},{3},,{4}\n".format(*data))
        f.write("\nmax spare capacity\n")
        for data in sp:
            f.write("{0},{1},{2},{3},,{4}\n".format(*data))
