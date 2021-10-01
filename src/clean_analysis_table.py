#!/usr/bin/env python3

# WS client example

import sys
import os
import argparse
import operator
import time
import json
import sqlite3
import moss_functions as moss


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='db_dir for moss directory')
args = parser.parse_args()

runningfile = args.input + "/analyticalFiles/runningAnalyses.json"

referencejson= dict()
with open(runningfile, 'w') as f_out:
    json.dump(referencejson, f_out)
f_out.close()

queuedfile = args.input + "/analyticalFiles/queuedAnalyses.json"

referencejson= dict()
with open(queuedfile, 'w') as f_out:
    json.dump(referencejson, f_out)
f_out.close()


#TBD: Here remove directories created, and perhaps look in the SQL db to remove anyhing that may have been placed there



