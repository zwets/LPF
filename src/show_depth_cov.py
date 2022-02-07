# Copyright (c) 2019, Malte Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries

import sys
import os
import argparse
import operator
import time
import gc
import numpy as np
import array
import subprocess
from optparse import OptionParser
from operator import itemgetter
import moss_functions as moss
import re
import json
import sqlite3
from matplotlib import pyplot as plt


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-mat', action="store", type=str, dest='mat', default="", help='Mat file')
parser.add_argument('-o', action="store", type=str, dest='out', default="", help='out. ')

args = parser.parse_args()

vector_dict = dict()
infile = open(args.mat, 'r')
current_seq = ""
for line in infile:
    line = line.rstrip()
    if len(line) > 0:
        if line[0] == "#":
            vector_dict[line] = []
            current_seq = line
        else:
            line = line.split()
            sum = 0
            for element in line[1:]:
                if int(element) > 0:
                    sum += int(element)
            vector_dict[current_seq].append(sum)

infile.close()

for item in vector_dict:
    a_list = list(range(1, len(vector_dict[item])+1))
    plt.plot(a_list, vector_dict[item])
    plt.title(item)
    plt.xlabel("Position")
    plt.ylabel("Depth")
    plt.show()
    plt.savefig('{}{}_plot.png'.format(args.out, item.split()[0]))



