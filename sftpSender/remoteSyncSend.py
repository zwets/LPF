#!/usr/bin/env python

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

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-username', action="store", type=str, dest='username', default="", help='Path.')
parser.add_argument('-password', action="store", type=str, dest='password', default="", help='Pttt')
parser.add_argument('-server', action="store", type=str, dest='server', default="", help='Patd ')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')
args = parser.parse_args()

username = args.username
password = args.password
server = args.server
dbdir = args.db_dir

class FastTransport(paramiko.Transport):
    def __init__(self, sock):
        super(FastTransport, self).__init__(sock)
        self.window_size = 2147483647
        self.packetizer.REKEY_BYTES = pow(2, 40)
        self.packetizer.REKEY_PACKETS = pow(2, 40)

ssh_conn = FastTransport((server, 22))
ssh_conn.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(ssh_conn)

with open(dbdir + "syncFiles/referenceSync.json") as json_file:
    referencejson = json.load(json_file)
json_file.close()

sftp.put(dbdir + "syncFiles/referenceSync.json", '/home/people/malhal/MOSS/current/malhal/referenceSync/referenceSync.json')


for key in referencejson:
    if key != 'timestamp':
        print (referencejson[key]['filename'])
        filepath = dbdir + "datafiles/isolatefiles/" + key + "/" + key

        sftp.put(filepath, '/home/people/malhal/MOSS/current/malhal/referenceCons/' + key)
        
with open(dbdir + "syncFiles/isolateSync.json") as json_file:
    isolatejson = json.load(json_file)
json_file.close()



sftp.put(dbdir + "syncFiles/isolateSync.json", '/home/people/malhal/MOSS/current/malhal/isolateSync/isolateSync.json')

for key in isolatejson:
    if key != 'timestamp':
        print (key)
        filepath = dbdir + "datafiles/isolatefiles/" + isolatejson[key]['refname'] + "/" + key + "_" + isolatejson[key]['refname'] + "_consensus.fsa"
        sftp.put(filepath, '/home/people/malhal/MOSS/current/malhal/isolateCons/' + key + "_consensus.fsa") #Fix isolatnavn
