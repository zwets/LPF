
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



parser = argparse.ArgumentParser(description='.')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='Path to your DB-directory')
# parser.add_argument('-isolate_file_path', action="store", type=str, dest='isolate_path', default="", help='Comlete path to the reference samples')
parser.add_argument('-o', action="store", type=str, dest='output', default="", help='Complete path to the isolates')
args = parser.parse_args()

conn = sqlite3.connect(args.input)
c = conn.cursor()
print ("refs")
reflist = (c.execute("SELECT header_text from refs")).fetchall()
for item in reflist:
    print (item[0])
print ("isolates")
isolatelist = (c.execute("SELECT header_text, samplename from isolates")).fetchall()
for item in isolatelist:
    print ("refrence: {} has isolatemapping; {}".format(item[0], item[1]))


conn.close()

complete_tree_dict = {}

for item in reflist:
    complete_tree_dict.setdefault(item[0], [])

for item in isolatelist:
    complete_tree_dict.setdefault(item[0], []).append(item[1])
print (complete_tree_dict)

for key in complete_tree_dict:
    print("|")
    if key == []:
        print("-{}".format(str(key)))
    else:
        print("-{}".format(str(key)))
        for value in complete_tree_dict[key]:
            print("\t|")
            print("\t-{}".format(str(value)))

