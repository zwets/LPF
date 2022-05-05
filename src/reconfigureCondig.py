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
parser.add_argument('-file', action="store", type=str, dest='file', default="", help='configFile to be reconfigured to your local machine.')
parser.add_argument('-localPath', action="store", type=str, dest='localPath', default="", help='local path to the directory in which you store the moss system! Not the installation directory, but the database directory!')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='Local path to where MOSS was install (Directory with the kma and ccphylo directories)')
args = parser.parse_args()

localPath = moss.correctPathCheck(args.localPath)
exepath = moss.correctPathCheck(args.exepath)

with open(args.file) as json_file:
    referencejson = json.load(json_file)
json_file.close()

referencejson["config_name"] = localPath

referencejson["exepath"] = exepath

with open(args.file, 'w') as f_out:
    json.dump(referencejson, f_out)
f_out.close()

