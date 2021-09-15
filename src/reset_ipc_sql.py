#!/usr/bin/env python3

# WS client example

import sys
import os
import argparse
import operator
import time
import json
import asyncio
import websockets
import paramiko
from scp import SCPClient
import moss_functions as moss


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='db_dir for moss directory')
args = parser.parse_args()

isolatedb = args.input + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()

dbstring = "UPDATE referencetable SET isolateid = '{}' WHERE headerid = '{}'".format(isolateid, templatename)
c.execute(dbstring)

conn.commit()
conn.close()

