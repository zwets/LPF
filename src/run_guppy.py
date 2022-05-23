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
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='input')
parser.add_argument('-name', action="store", type=str, dest='name', default="", help='name')
parser.add_argument('-bk', action="store", type=str, dest='bk', default="", help='bk')
parser.add_argument('-chunks', action="store", type=str, dest='chunks', default="", help='chunks')
parser.add_argument('-c', action="store", type=str, dest='model', default="", help='model')
args = parser.parse_args()

def main(args):
    check_input_name(args)
    base_call(args)
    sys.exit("HERE")
    fast5_path = concat_input(args)
    os.system("mkdir /opt/moss_data/fastq/{}".format(args.name))
    cmd = "/opt/moss/ont-guppy/bin/./guppy_basecaller -i {}/  -s /opt/moss_data/fastq/{}/ --device \"cuda:0\" --compress_fastq --trim_barcodes -c {}".format(fast5_path, args.name, args.model)
    if args.chunks != "":
        cmd += " --chunks_per_runner 75"
    if args.bk != "":
        cmd += " --barcode_kits \"{}\"".format(args.bk)
    print (cmd)
    os.system(cmd)

def check_input_name(args):
    files = os.listdir("/opt/moss_data/fast5/")
    if args.name in files:
        sys.exit("This experiment name has already been used. Please choose another one.")

def base_call(args):
    cmd = "/opt/moss/ont-guppy/bin/./guppy_basecaller -i {}  -s /opt/moss_data/fastq/{}/--device \"cuda:0\" --compress_fastq --trim_barcodes -c {}".format(args.input, args.name, args.model)
    os.system(cmd)

def concat_input(args):
    files = os.listdir(args.input)
    barcode_folder = list()
    for item in files:
        if "barcode".upper() in item.upper():
            barcode_folder.append(item)
    print (barcode_folder)
    if len(barcode_folder) == 0:
        sys.exit("There are no barcode folders in the pass fast5 folder you provided. Please check and make sure the content of the provided fast5 pass folder in correct.")
    os.system("mkdir /opt/moss_data/fast5/{}".format(args.name))
    for item in barcode_folder:
        os.system("cat {}/{}/*.fast5* > /opt/moss_data/fast5/{}/{}_{}.fast5".format(args.input, item, args.name, args.name, item))
    return ("/opt/moss_data/fast5/{}/".format(args.name))

if __name__ == '__main__':
    main(args)