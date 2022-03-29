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
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')
args = parser.parse_args()

db_dir = args.db_dir

with open("{}static_files/runningAnalyses.json".format(db_dir), 'w') as f_out:
    json.dump(dict(), f_out)
f_out.close()

with open("{}static_files/queuedAnalyses.json".format(db_dir), 'w') as f_out:
    json.dump(dict(), f_out)
f_out.close()


