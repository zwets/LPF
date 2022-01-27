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
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3


#Give path to database directory
#Give initial files for references
#Give directories with isolates corresponing to references
#In database directory make two directories, one for KMA DB and one for MIONT-DB



parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-reference_files_path', action="store", type=str, dest='reference_path', default="", help='Path to your DB-directory')
parser.add_argument('-isolate_file_path', action="store", type=str, dest='isolate_path', default="", help='Comlete path to the reference samples')
parser.add_argument('-db_dir_path', action="store", type=str, dest='db_dir_path', default="", help='Complete path to the isolates')
args = parser.parse_args()


conn = sqlite3.connect('MinION-Typer.db')
c = conn.cursor()


c.execute("SELECT header_text from refs")
references = c.fetchall()





c.execute("SELECT header_text, samplename from isolates")
isolates = c.fetchall()
#c.execute("SELECT id, header_text, samplename from isolates")print (c.fetchall())

for i in range(5, len(references)):
    print("For " + references[i][0] + " the following are isolates: ")
    for t in range(len(isolates)):
        if references[i][0] == isolates[t][0]:
            print (isolates[t][1])

#for i in range(len(references)):

conn.commit()
conn.close()