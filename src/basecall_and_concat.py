#!/usr/bin/env python3

# Copyright (c) 2019, Malte Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries

import sys
import os
import argparse
import operator
import random
import subprocess
import time
import gc
import numpy as np
import array
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3
import moss_functions as moss
import json
from joblib import Parallel, delayed
#Use Argparse to correctly open the inputfiles

# create the parser for the "surveillance" command


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-i', action="store", type=str, dest='input_path', default="", help='input_path')
parser.add_argument('-n', action="store", type=str, dest='name', default="", help='name')
parser.add_argument('-d', action="store", type=str, dest='directory', default="", help='directory')
parser.add_argument('-bk', action="store", type=str, dest='bk', default="", help='bk')
parser.add_argument('-chunks', action="store", type=str, dest='chunks', default="", help='chunks')
parser.add_argument('-c', action="store", type=str, dest='model', default="", help='model')
parser.add_argument("-exepath", action="store", dest="exepath", default = "", help="Complete path to the moss repo that you cloned, in which your kma and ccphylo folder at located.")
args = parser.parse_args()

directory = args.directory

cmd = "{}ont-guppy/bin/./guppy_basecaller -i {}  -s {} --device \"cuda:0\" --compress_fastq --trim_barcodes -c {}".format(args.exepath, args.input_path, args.directory, args.model)
if args.chunks != "":
    cmd += " --chunks_per_runner 75"
if args.bk != "":
    cmd += " --barcode_kits \"{}\"".format(args.bk)

os.system(cmd)
cmd = "cat {}/pass/* > {}{}.fastq.gz".format(args.directory, args.directory, args.name)
os.system(cmd)