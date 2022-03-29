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
#Use Argparse to correctly open the inputfiles

# create the parser for the "surveillance" command


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='metadata csv file')
parser.add_argument("-jobs", type=int, action="store", dest="jobs", default = 1, help="Number of jobs to be run in parallel. Default is 4. Consider your computational capabilities!")
parser.add_argument("-threads", type=int, action="store", dest="threads", default = 1, help="threads")
parser.add_argument("-input_type", type=str, action="store", dest="input_type", default = "", help="input_type")
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='configname')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='exepath')
args = parser.parse_args()

def mossAnalysis(jobslist, i):
    os.system(jobslist[i]) #Jobs not queued yet- fix

def main(input, jobs, threads, input_type, configname, exepath):

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
        cmd = "python3 {}/src/moss.py -seqType {} -configname {} -thread {} -exepath {} -metadata \"{}\" -metadata_headers \"{}\"".format(exepath, input_type, configname, threads, exepath, ",".join(infile_matrix[i+1]), ",".join(infile_matrix[0]))
        jobslist.append(cmd)
        metadata_dict = moss.prod_metadata_dict(",".join(infile_matrix[i + 1]), ",".join(infile_matrix[0]))
        input = metadata_dict['input'].split()[0]
        entryid = moss.md5(input)
        moss_sql.init_status_table(entryid, "Queued", "Not Determined", "0", "10", "Queued", configname)

    Parallel(n_jobs=jobs)(delayed(mossAnalysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
  main(args.input, args.jobs, args.threads, args.input_type, args.configname, args.exepath)

