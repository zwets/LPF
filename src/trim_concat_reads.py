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
parser.add_argument('-n', action="store", type=str, dest='name', default="", help='name')
parser.add_argument('-d', action="store", type=str, dest='directory', default="", help='directory')
args = parser.parse_args()

directory = args.directory

cmd = "cat {}/fail/* > {}{}.fastq.gz".format(args.directory, args.directory, args.name)
os.system(cmd)