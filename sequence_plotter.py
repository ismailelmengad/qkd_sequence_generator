# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 10:31:35 2022

@author: 15164
"""

#!/usr/bin/env python
from __future__ import print_function, division
import numpy as np
import contextlib
import matplotlib.pyplot as plt
from itertools import cycle, islice
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
    parser.add_argument("-o", "--output", type=str, default="-", help="CSV file updated with delayed values")
    #parser.add_argument("--infile", type=str, default="-", help="CSV file to plot from")
    parser.add_argument("--outplot", type=str, default="-", help="Plot file showing delays")
    parser.add_argument("-d1", "--delay1", type=int, default=0, help="Number of time bins to delay channel 1 by")
    parser.add_argument("-d2", "--delay2", type=int, default=0, help="Number of time bins to delay channel 2 by")
    parser.add_argument("-d3", "--delay3", type=int, default=58, help="Number of time bins to delay channel 3 by")
    parser.add_argument("-d4", "--delay4", type=int, default=0, help="Number of time bins to delay channel 4 by")
    parser.add_argument("-s", "--sample-rate", type=float, default=85.75, help="sample rate in GHz")
    parser.add_argument("--samples", type=int, default=255360, help="total number of samples")
    parser.add_argument("--sequence", nargs='+', default=None, help="manual sequence")
    parser.add_argument("--output-sequence", default="-", help="output sequence file")
    parser.add_argument("-f", "--frequency", type=float, default=6.125, help="pulse repetition rate in GHz")
    parser.add_argument("-n", "--num-qubits", type=int, default=10, help="number of qubits")
    parser.add_argument("--duty-cycle", type=float, default=0.2, help="fraction of pulse period that is high")
    parser.add_argument("--plot", action='store_true', default=False, help="plot the waveforms")
    parser.add_argument("--time-basis-probability", type=float, default=0.9, help="probability to output a time basis qubit")
    parser.add_argument("--phase-levels", type=int, default=5, help="number of phase randomization levels")
    parser.add_argument("--phase-scale", type=int, default=0.1, help="increase in output for each phase level")
    
    args = parser.parse_args()
    
    if (args.delay1 < 0) or (args.delay2 < 0) or (args.delay3 < 0) or (args.delay4 < 0):
        print("error: delays should be non-negative integers", file=sys.stderr)
        sys.exit(1)

    t = np.linspace(0,args.samples/args.sample_rate,args.samples)
    
    p = [args.time_basis_probability/2]*2 + [1-args.time_basis_probability] + [0.0]

    if args.sequence is not None:
        for qubit in args.sequence:
            if qubit not in ["E","L","P","0"]:
                print("error: don't understand qubit '%s'" % qubit, file=sys.stderr)
                print("must be one of 'E', 'L', 'P', or '0'", file=sys.stderr)
                sys.exit(1)

        sequence = np.array(list(islice(cycle(args.sequence),None,args.num_qubits)),dtype='<U1')
    else:
        sequence = np.random.choice(["E","L","P","0"],size=args.num_qubits,p=p)

    phase_sequence = np.random.choice(np.arange(args.phase_levels),size=args.num_qubits)

    with smart_open(args.output_sequence) as f:
        f.write("".join(sequence) + '\n')
        print("Printed to output sequence file")

    y1 = np.zeros(args.samples)
    y2 = np.zeros(args.samples)
    y3 = np.zeros(args.samples)
    y4 = np.zeros(args.samples)
    y5 = np.zeros(args.samples)
    for i in range(len(y1)):
        bit, remainder = np.divmod(t[i],1/args.frequency)
        bit = int(bit)

        if i < 100:
            y1[i] = 1

        if bit >= len(sequence):
            continue

        if remainder > args.duty_cycle/args.frequency:
            continue

        y2[i] = phase_sequence[bit]*args.phase_scale

        if sequence[bit] == 'E':
            y3[i] = 1
            y4[i] = 0
        elif sequence[bit] == 'L':
            y3[i] = 0
            y4[i] = 1
        elif sequence[bit] == 'P':
            y3[i] = 0.5
            y4[i] = 0.5
            
    
    with smart_open(args.output) as f:
        f.write("SampleRate = %.3f GHz\n" % args.sample_rate)
        for i in range(len(y1)):
            f.write(",".join(["%.18g" % x for x in [y1[i], y2[i], y3[i], y4[i]]]) + '\n')
        f.close()
    
    with open(args.output) as f:
        csv_file = csv.reader(f)
        line_counter=0
        for lines in csv_file:
            if (line_counter > 1) and (line_counter < args.samples):
                y1[line_counter] = float(lines[0])
                y2[line_counter] = float(lines[1])
                y3[line_counter] = float(lines[2])
                y4[line_counter] = float(lines[3])
            line_counter += 1

    clock_start=min(args.delay3, args.delay4)
    start_index=max(args.delay1, args.delay2, args.delay3, args.delay4)
    
    channel_1_delay = np.empty(0)
    for i in range(args.delay1):
        channel_1_delay = np.append(0, channel_1_delay)
        y2 = np.append(y2, 0)
    clock_channel = np.concatenate((channel_1_delay, y1))
   
    channel_2_delay = np.empty(0)
    for i in range(args.delay2):
        channel_2_delay = np.append(0, channel_2_delay)
        clock_channel = np.append(clock_channel, 0)
    phase_channel = np.concatenate((channel_2_delay, y2)) 
   
    channel_3_delay = np.empty(0)
    for i in range(args.delay3):
        channel_3_delay = np.append(0, channel_3_delay)
        y4 = np.append(y4, 0)
    early_channel = np.concatenate((channel_3_delay, y3))
    
    channel_4_delay = np.empty(0)
    for i in range(args.delay4):
        channel_4_delay = np.append(0, channel_4_delay)
        early_channel = np.append(early_channel, 0)
    late_channel = np.concatenate((channel_4_delay, y4))
    
    
    
    time_bin_counter = 0
    for i in range(len(y5)):
        if (time_bin_counter % 15 == 0) and (y5[i] == 0):
            y5[i:i+7] += 1
            time_bin_counter += 1
        elif (time_bin_counter % 15 == 0) and (y5[i] == 1):
            y5[i] = 0
            time_bin_counter += 1
            
        time_bin_counter += 1
    
    for i in range(clock_start):
        y5 = np.append(0, y5)
        
    for i in range(start_index):
        clock_channel= np.append(clock_channel, 0)
        phase_channel= np.append(phase_channel, 0)
        y5 = np.append(y5, 0)
    
    '''
    print("The length of y%d is %d\n" % (1, len(clock_channel)))
    print("The length of y%d is %d\n" % (2, len(phase_channel)))
    print("The length of the early channel is %d\n" % len(early_channel))
    print("The length of the late channel is %d\n" % len(late_channel))
    print("The length of y%d is %d\n" % (5, len(y5)))
    '''
    
    with smart_open(args.output) as f:
        f.write("SampleRate = %.3f GHz\n" % args.sample_rate)
        f.write("Y1,Y2,Y3,Y4\n")
        for i in range(len(y1)):
            f.write(",".join(["%.18g" % x for x in [y1[i], y2[i], early_channel[i], late_channel[i]]]) + '\n')
        f.close()    
    
    if args.plot:
        with smart_open(args.outplot) as f:
            print("Plotting %s\n" % f)
            fig, ax = plt.subplots(4,1)
            
            ax[0].plot(t[:200], clock_channel[:200])
            ax[0].set_xlim(t[0],t[200])
            ax[0].set_title('Channel 1 (Clock)')
                
            ax[1].plot(t[:200], phase_channel[:200])
            ax[1].set_xlim(t[0],t[200])
            ax[1].set_title('Channel 2 (Phase)')
                
            ax[2].plot(t[:200], early_channel[:200])
            ax[2].set_xlim(t[0],t[200])
            ax[2].set_title('Channel 3 (Early)')
                
            ax[3].plot(t[:200], late_channel[:200])
            ax[3].set_xlim(t[0],t[200])
            ax[3].set_title('Channel 4 (Late)')
                
            plt.subplots_adjust(top=0.8,
                                bottom=0.2,
                                hspace=2.2)
               
            fig.savefig(args.outplot)

            