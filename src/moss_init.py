# Copyright (c) 2019, Malte Hallgren Technical University of Denmark
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


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-kmaindex_db_path', action="store", type=str, dest='kmaindex_db_path', default="", help='Path a .ATG kma-index database that is desired to be used a references. It is expected that both the .ATG.name file and .ATG.seq.b file is present in this directory, and that NO OTHER files are present. http://www.cbs.dtu.dk/public/CGE/databases/KmerFinder/version/20190108_stable/ link to bacteria.tar.gz, which is a good option for a starting database')
parser.add_argument("-config_name", action="store", dest="config_name", help="Enter a name for your configuration file.")

args = parser.parse_args()

"/opt/moss/kma/kma" = "/opt/moss/kma/kma"
config_name = args.config_name

kmaindex_db_path = moss.correctPathCheck(args.kmaindex_db_path)

if not os.path.exists("/opt/moss_db"):
    sys.exit("MOSS has not been correctly initialized. no /opt/moss_db exists")

if not os.path.exists("/opt/moss_db/{}".format(config_name)):
    os.system("mkdir /opt/moss_db/{}".format(config_name))
else:
    sys.exit("A moss database of that name already exists on this computer!")

config_name = "/opt/moss_db/{}/".format(config_name)

print ("cloning reference DB, if you are using a big reference DB, this might take a while")
os.system("cp {}*.ATG.comp.b {}REFDB.ATG.comp.b".format(kmaindex_db_path, config_name))
os.system("cp {}*.ATG.length.b {}REFDB.ATG.length.b".format(kmaindex_db_path, config_name))
os.system("cp {}*.ATG.seq.b {}REFDB.ATG.seq.b".format(kmaindex_db_path, config_name))
os.system("cp {}*.ATG.name {}REFDB.ATG.name".format(kmaindex_db_path, config_name))
print ("cloning reference DB complete")

directory_structure = {
    "analysis": {},
    "metadata_csv": {},
    "consensus_sequences": {},
    "basecall_output": {},
    "sync_files": {},
    "static_files": {},
    "datafiles": {}

}
moss.create_directory_from_dict(directory_structure, config_name)


conn = sqlite3.connect(config_name + 'moss.db')
c = conn.cursor()

metadata_string = ""
infile = open("/opt/moss/datafiles/ENA_list.csv", 'r')
for line in infile:
    if '\ufeff' in line:
        line = line.replace(u'\ufeff', '').split(",")
    else:
        line = line.split(",")
    for item in line:
        metadata_string += "{} TEXT,".format(item)
infile.close()
metadata_string = metadata_string[:-1]

c.execute("""CREATE TABLE IF NOT EXISTS sample_table(entryid TEXT PRIMARY KEY, sample_name TEXT, reference_id TEXT, amr_genes TEXT, virulence_genes TEXT, plasmids TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS reference_table(entryid TEXT PRIMARY KEY, reference_header_text TEXT)""") #Mangler finder results. Implement eventually
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS metadata_table(entryid TEXT PRIMARY KEY, {})""".format(metadata_string))
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS ipc_table(ipc TEXT PRIMARY KEY, ipc_index_refdb TEXT, IsolateJSON TEXT, ReferenceJSON TEXT, ReadRefDB TEXT, running_analyses TEXT, queued_analyses TEXT, finished_analyses TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS status_table(entryid TEXT PRIMARY KEY, status TEXT, type TEXT, current_stage TEXT, final_stage TEXT, result TEXT, time_stamp TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS local_sync_table(entryid TEXT PRIMARY KEY, time_of_analysis TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS basecalling_table(name TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT)""")
conn.commit()
dbstring = "INSERT INTO ipc_table(ipc, ipc_index_refdb, ReadRefDB, running_analyses, queued_analyses, finished_analyses) VALUES('{}' ,'{}', '{}', '{}', '{}', '{}')".format('IPC',1, 100, "", "", "")
c.execute(dbstring)
conn.commit()
conn.close()
#Can we add tables for genes with pointers? Better solution!


moss.init_insert_reference_table(config_name)

# Generate config.json file
jsondict = dict()
jsondict["current_working_db"] = args.config_name
with open("/opt/moss_db/config.json", 'w') as f_out:
  json.dump(jsondict, f_out)
f_out.close()

cmd = "python3 /opt/moss/src/createGuppyWorkflowDict.py -current_working_db {}".format(args.config_name)
os.system(cmd)