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



parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')

args = parser.parse_args()

#Load previous file, needs to be done

isolatedb = args.db_dir + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM referencetable")
reference_db_size = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM isolatetable")
child_db_size = c.fetchone()[0]
#Last sync to external db


childnames = []
for i in range(len(parentlist)):
    isolateids = parentlist[i][3].split(", ")
    for i in range(len(isolateids)):
        c.execute("SELECT samplename FROM isolatetable WHERE entryid = '{}'".format(isolateids[i]))
        isolateids[i] = c.fetchone()[0]
    isolateids = ", ".join(isolateids)
    childnames.append(isolateids)

conn.close()



parentdict = dict()
for i in range(len(parentlist)):
    parentdict[parentlist[i][1]] = childnames[i]
od = collections.OrderedDict(sorted(parentdict.items()))

with open(args.db_dir + 'analyticalFiles/databaseviewer.json', 'w') as fp:
    json.dump(od, fp)



