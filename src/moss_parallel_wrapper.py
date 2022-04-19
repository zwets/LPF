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
import moss_sql as moss_sql
import json
from joblib import Parallel, delayed
#Use Argparse to correctly open the csvfiles

# IMPORTANT: SYSTEM IS NOT TESTED FOR STABILITY FOR MASSIVE PARALLEL USAGE YET!


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-csv', action="store", type=str, dest='csv', default="", help='metadata csv file')
parser.add_argument("-jobs", type=int, action="store", dest="jobs", default = 1, help="Number of jobs to be run in parallel. Default is 4. Consider your computational capabilities!")
parser.add_argument("-threads", type=int, action="store", dest="threads", default = 4, help="threads. Default is 4. Assumes people have decent hardware. Potentially increase and test.")
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='configname')
args = parser.parse_args()

def mossAnalysis(jobslist, i):
    os.system(jobslist[i]) #Jobs not queued yet- fix

def main(csv, jobs, threads, configname):

    with open(csv, 'r') as f:
        line = f.read()
        print (line)

    sys.exit()

    infile = open(csv, 'r')
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

    if jobs > 8:
        sys.exit("Currently a maximum of 8 jobs are permitted in parallel.")

    filelist = []
    jobslist = []
    for i in range(len(infile_matrix)-1):
        filelist.append(infile_matrix[i+1][0])
        cmd = "python3 {}/src/moss.py -seqType {} -configname {} -thread {} -metadata \"{}\" -metadata_headers \"{}\"".format(configname, threads, ",".join(infile_matrix[i+1]), ",".join(infile_matrix[0]))
        jobslist.append(cmd)
        metadata_dict = moss.prod_metadata_dict(",".join(infile_matrix[i + 1]), ",".join(infile_matrix[0]))
        csv = metadata_dict['csv'].split()[0]
        entryid = moss.md5(csv)
        moss_sql.init_status_table(entryid, "Queued", "Not Determined", "0", "10", "Queued", configname)

    Parallel(n_jobs=jobs)(delayed(mossAnalysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
  main(args.csv, args.jobs, args.threads, args.configname)

