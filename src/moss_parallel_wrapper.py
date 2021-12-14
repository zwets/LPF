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
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='metadata csv file')
parser.add_argument("-jobs", type=int, action="store", dest="jobs", default = 1, help="Number of jobs to be run in parallel. Default is 4. Consider your computational capabilities!")
parser.add_argument("-threads", type=int, action="store", dest="threads", default = 1, help="threads")
parser.add_argument("-input_type", type=str, action="store", dest="input_type", default = "", help="input_type")
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='db_dir')
parser.add_argument("-mac", action="store_true", default = False, dest="mac", help="when using a mac - DB not loaded to shm")
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='exepath')
args = parser.parse_args()

def mossAnalysis(jobslist, i):
    os.system(jobslist[i]) #Jobs not queued yet- fix

def main(input, jobs, threads, input_type, db_dir, exepath, mac):

    infile = open(input, 'r')
    infile_matrix = []
    for line in infile:
        line = line.rstrip()
        print (line)
        if ";" in line:
            line = line.split(";")
        elif "," in line:
            line = line.split(",")
        infile_matrix.append(line)
    infile.close()


    #here continue

    if jobs > 8:
        sys.exit("Currently a maximum of 8 jobs are permitted in parallel.")

    filelist = []
    jobslist = []
    for i in range(len(infile_matrix)-1):
        filelist.append(infile_matrix[i+1][0])
        cmd = "python3 {}/src/moss.py -seqType {} -db_dir {} -thread {} -exepath {} -metadata \"{}\" -metadata_headers \"{}\"".format(exepath, input_type, db_dir, threads, exepath, ",".join(infile_matrix[i+1]), ",".join(infile_matrix[0]))
        if mac:
            cmd += " -mac"
        jobslist.append(cmd)

    for item in jobslist:
        print (item)
    Parallel(n_jobs=jobs)(delayed(mossAnalysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
  main(args.input, args.jobs, args.threads, args.input_type, args.db_dir, args.exepath, args.mac)

