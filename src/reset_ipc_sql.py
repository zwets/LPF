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
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='config_name for moss directory')
args = parser.parse_args()

isolatedb = args.input + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()
dbstring = "UPDATE ipc_table SET ipc_index_refdb = 1, IsolateJSON = 1, ReferenceJSON = 1, ReadRefDB = 100, running_analyses = \"\", queued_analyses = \"\""
c.execute(dbstring)

conn.commit()
conn.close()

