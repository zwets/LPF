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
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='configname for moss directory')
args = parser.parse_args()

isolatedb = args.input + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()
#c.execute("""CREATE TABLE IF NOT EXISTS ipc_table(ipc_index_refdb TEXT, IsolateJSON TEXT, ReferenceJSON TEXT, ReadRefDB TEXT, running_analyses TEXT, queued_analyses TEXT, finished_analyses TEXT)""")
#dbstring = "UPDATE ipc_table SET ipc_index_refdb = '{}'".format(1)
dbstring = "UPDATE ipc_table SET ipc_index_refdb = 1, IsolateJSON = 1, ReferenceJSON = 1, ReadRefDB = 100, running_analyses = \"\", queued_analyses = \"\""
c.execute(dbstring)

conn.commit()
conn.close()

