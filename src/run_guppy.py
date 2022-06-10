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
    data_format = check_input_name(args)
    os.system("mkdir /opt/moss_data/fastq/{}".format(args.name))
    base_call(args, data_format)

def check_input_name(args):
    data_format = None
    files = os.listdir("/opt/moss_data/fast5/")
    if args.name in files:
        sys.exit("This experiment name has already been used. Please choose another one.")
    files_list = os.listdir(args.input)
    if "barcode" in args.name: #assume there wouldn't randomly be a barcode named folder elsewhere
        args.name = "/".join(args.split("/")[0:-2]) + "/" #Assume
    elif "fast5" in files_list:
        data_format = "fast5s"
    else:
        sys.exit("Neither a folder with barcodes folders or a folder with many fast5s were given.")
    return data_format

def base_call(args, data_format):
    if data_format == "fast5s":
        cmd = "/opt/ont/guppy/bin/guppy_basecaller -i {}  -s /opt/moss_data/fastq/{}/ --device \"cuda:0\" --compress_fastq --trim_barcodes -c {} --barcode_kits {}".format(
            args.input, args.name, args.model, args.bk)
        os.system(cmd)
        os.system("rm -rf /opt/moss_data/fastq/{}/*.fast5".format(args.name))
        os.system("mkdir/opt/moss_data/fastq/{}/final/".format(args.name))
        file_list = "/opt/moss_data/fastq/{}/".format(args.name)
        if "pass" in file_list:
            files = os.listdir("/opt/moss_data/fastq/{}/pass/".format(args.name))
            barcode_list = []
            for item in files:
                if "barcode".upper() in item.upper():
                    barcode_list.append("/opt/moss_data/fastq/{}/pass/".format(args.name) + item)
        else:
            files = os.listdir("/opt/moss_data/fastq/{}/".format(args.name))
            barcode_list = []
            for item in files:
                if "barcode".upper() in item.upper():
                    barcode_list.append("/opt/moss_data/fastq/{}/pass".format(args.name) + item)
        for item in barcode_list:
            os.system(
                "cat {}/*.fastq.gz > /opt/moss_data/fastq/{}/{}_{}.fastq.gz".format(
                    item, args.name, args.name, item.split("/")[-2]))
            os.system("rm -rf /opt/moss_data/fastq/{}/pass".format(args.name))
    else:
        files = os.listdir(args.input)
        barcode_list = list()
        for item in files:
            if "barcode".upper() in item.upper():
                barcode_list.append(item)
        print (len(barcode_list))
        for item in barcode_list:
            cmd = "/opt/ont/guppy/bin/guppy_basecaller -i {}/{}  -s /opt/moss_data/fastq/{}/{} --device \"cuda:0\" --compress_fastq --trim_barcodes -c {}".format(args.input, item, args.name, item, args.model)
            print(cmd)
            os.system(cmd)
        for item in barcode_list:
            os.system("cat /opt/moss_data/fastq/{}/{}/pass/*.fastq.gz > /opt/moss_data/fastq/{}/{}_{}.fastq.gz".format(args.name, item, args.name, args.name, item))
            os.system("rm -rf /opt/moss_data/fastq/{}/{}/pass/".format(args.name, item))
if __name__ == '__main__':
    main(args)