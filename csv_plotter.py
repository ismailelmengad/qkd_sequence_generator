# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 13:58:30 2022

@author: 15164
"""

#!/usr/bin/env python
from __future__ import print_function, division
import numpy as np
import contextlib
import matplotlib.pyplot as plt
import csv

@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser("generate plots from QKD csv files")
    parser.add_argument("--infile", type=str, default="-", help="CSV file from which the plot will be made")
    parser.add_argument("-o", "--output", type=str, default="-", help="File which plots will save to")
    parser.add_argument("--samples", type=int, default=255360, help="total number of samples")
    parser.add_argument("-s", "--sample-rate", type=float, default=85.75, help="sample rate in GHz")

    args = parser.parse_args()

    t = np.linspace(0,args.samples/args.sample_rate,args.samples)

    y1 = np.zeros(args.samples)
    y2 = np.zeros(args.samples)
    y3 = np.zeros(args.samples)
    y4 = np.zeros(args.samples)
    
    with open(args.infile) as f:
        csv_file = csv.reader(f)
        line_counter = 0
        for lines in csv_file:
            # print("Getting line %d / %d" % (line_counter, args.samples))
            if (line_counter >= 2) and (line_counter <= args.samples - 10):
                y1[line_counter] = float(lines[0])
                y2[line_counter] = float(lines[1])
                y3[line_counter] = float(lines[2])
                y4[line_counter] = float(lines[3])
            line_counter += 1

            
        print("The length of y1 is %d\n" % len(y1))
        print("The length of y2 is %d\n" % len(y2))
        print("The length of y3 is %d\n" % len(y3))
        print("The length of y4 is %d\n" % len(y4))
    
    with smart_open(args.output) as f:
        print("Plotting from %s\n" % f)
        fig, ax = plt.subplots(4,1)
                
        ax[0].plot(t[:200], y1[:200])
        ax[0].set_xlim(t[0],t[200])
        ax[0].set_title('Channel 1 (Clock)')
                
        ax[1].plot(t[:200], y2[:200])
        ax[1].set_xlim(t[0],t[200])
        ax[1].set_title('Channel 2 (Phase)')
                
        ax[2].plot(t[:200], y3[:200])
        ax[2].set_xlim(t[0],t[200])
        ax[2].set_title('Channel 3 (Early)')
                
        ax[3].plot(t[:200], y4[:200])
        ax[3].set_xlim(t[0],t[200])
        ax[3].set_title('Channel 4 (Late)')
                
        plt.subplots_adjust(top=0.8,
                            bottom=0.2,
                            hspace=2.2)
               
        fig.savefig(args.output)

            