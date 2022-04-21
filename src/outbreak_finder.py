# Copyright (c) 2019, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries

import sys
import os
import argparse
import operator
import time
import gc
import numpy as np
import array
import subprocess
from optparse import OptionParser
from operator import itemgetter
import moss_functions as moss
import re
import json
import sqlite3
import collections


#Give path to database directory
#Give initial files for references
#Give directories with isolates corresponing to references
#In database directory make two directories, one for KMA DB and one for MIONT-DB



parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='Path to your DB-directory')

args = parser.parse_args()

isolatedb = args.configname + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()

c.execute("SELECT * FROM isolate_table")
referencelist = c.fetchall()
phylo_dict = dict()
for item in referencelist:
    if item[2] in phylo_dict:
        phylo_dict[item[2]].append(item[1])
    else:
        phylo_dict[item[2]] = [item[1]]


with open(args.configname + 'static_files/outbreakfinder.json', 'w') as fp:
    json.dump(phylo_dict, fp)



