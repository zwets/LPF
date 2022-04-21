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

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-csv', action="store", type=str, dest='csv', default="", help='metadata csv file')
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='configname')
args = parser.parse_args()

def main(csv):

    with open(csv, 'r') as f:
        data = f.read().split("\n")[0:-1]

    outfile = open("/opt/moss_db/testttttt", 'w')
    print (data, file=outfile)
    outfile.close()

if __name__== "__main__":
  main(args.csv)

