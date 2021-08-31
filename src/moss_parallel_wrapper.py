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
parser.add_argument('-i', action="store", type=str, dest='input', default="", help=';-Seperated string of commands')
parser.add_argument("-jobs", type=int, action="store", dest="jobs", default = 1, help="Number of jobs to be run in parallel. Default is 4. Consider your computational capabilities!")
args = parser.parse_args()

def mossAnalysis(inputlist, i):
    os.system(inputlist[i]) #Jobs not queued yet- fix

def main(input, jobs):

    if jobs > 8:
        sys.exit("Currently a maximum of 8 jobs are permitted in parallel")
    inputlist = input.split(";")



    filelist = []
    dbdir = ""
    for item in inputlist:
        tmplist = item.split()
        for i in range(len(tmplist)):
            if tmplist[i] == "-db_dir":
                dbdir = tmplist[i+1]
            if tmplist[i] == "-i":
                filelist.append(tmplist[i+1])


    moss.queueMultiAnalyses(dbdir, filelist)

    Parallel(n_jobs=jobs)(delayed(mossAnalysis)(inputlist, i) for i in range(len(inputlist)))
    print ("Analysis complete")

if __name__== "__main__":
  main(args.input, args.jobs)

