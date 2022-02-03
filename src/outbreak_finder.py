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
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')

args = parser.parse_args()

isolatedb = args.db_dir + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()

c.execute("SELECT * FROM isolatetable")
referencelist = c.fetchall()
phylo_dict = dict()
for item in referencelist:
    print (item)
sys.exit()


samplenames = []
for i in range(len(referencelist)):
    isolateids = referencelist[i][1].split(", ")
    for i in range(len(isolateids)):
        c.execute("SELECT samplename FROM isolatetable WHERE entryid = '{}'".format(isolateids[i]))
        isolateids[i] = c.fetchone()[0]
    isolateids = ", ".join(isolateids)
    samplenames.append(isolateids)

conn.close()



referencedict = dict()
for i in range(len(referencelist)):
    referencedict[referencelist[i][1]] = samplenames[i]
od = collections.OrderedDict(sorted(referencedict.items()))

with open(args.db_dir + 'analyticalFiles/outbreakfinder.json', 'w') as fp:
    json.dump(od, fp)



