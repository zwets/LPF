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
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='Path to your DB-directory')
args = parser.parse_args()

configname = args.configname

with open("{}static_files/runningAnalyses.json".format(configname), 'w') as f_out:
    json.dump(dict(), f_out)
f_out.close()

with open("{}static_files/queuedAnalyses.json".format(configname), 'w') as f_out:
    json.dump(dict(), f_out)
f_out.close()


