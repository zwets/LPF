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
import datetime
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
parser.add_argument('-config_name', action="store", type=str, dest='config_name', default="", help='config_name')
args = parser.parse_args()

def mossAnalysis(jobslist, i):
    os.system(jobslist[i]) #Jobs not queued yet- fix

def main(csv, jobs, config_name):

    with open(csv, 'r') as f:
        line = f.read().split("\n")[0:-1]
        metadata_headers = line[0]
        metadata_list = line[1:]
        input_dir = metadata_list[0].split(",")[-1]

    if jobs > 8:
        sys.exit("Currently a maximum of 8 jobs are permitted in parallel.")

    jobslist = []

    for i in range(len(metadata_list)):
        cmd = "python3 /opt/moss/src/moss.py -config_name {} -metadata \"{}\" -metadata_headers \"{}\"".format(config_name, metadata_list[i], metadata_headers)
        jobslist.append(cmd)
        input = metadata_list[i].split(",")[-2]
        sample_name = metadata_list[i].split(",")[1]
        entry_id = moss.md5(input)
        moss.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status, type, current_stage, final_stage, result, time_stamp) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
            .format(entry_id, sample_name, "Queued", "Queued", "Queued", "Queued", "Queued", ""), config_name)

    Parallel(n_jobs=jobs)(delayed(mossAnalysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
  main(args.csv, args.jobs, args.config_name)

