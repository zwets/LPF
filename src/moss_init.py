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
parser.add_argument("-configname", action="store", dest="configname", help="Enter a name for your configuration file.")

args = parser.parse_args()

kma_path = "/opt/moss/kma/kma"
configname = args.configname

kmaindex_db_path = moss.correctPathCheck(args.kmaindex_db_path)

if not os.path.exists("/opt/moss_db"):
    sys.exit("MOSS has not been correctly initialized. no /opt/moss_db exists")

if not os.path.exists("/opt/moss_db/{}".format(configname)):
    os.system("mkdir /opt/moss_db/{}".format(configname))
else:
    sys.exit("A moss database of that name already exists on this computer!")

configname = "/opt/moss_db/{}/".format(configname)

print ("cloning reference DB, if you are using a big reference DB, this might take a while")
os.system("cp {}*.ATG.comp.b {}REFDB.ATG.comp.b".format(kmaindex_db_path, configname))
os.system("cp {}*.ATG.length.b {}REFDB.ATG.length.b".format(kmaindex_db_path, configname))
os.system("cp {}*.ATG.seq.b {}REFDB.ATG.seq.b".format(kmaindex_db_path, configname))
os.system("cp {}*.ATG.name {}REFDB.ATG.name".format(kmaindex_db_path, configname))
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
moss.create_directory_from_dict(directory_structure, configname)


conn = sqlite3.connect(configname + 'moss.db')
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

c.execute("""CREATE TABLE IF NOT EXISTS isolatetable(entryid TEXT PRIMARY KEY, samplename TEXT, header_text TEXT, analysistimestamp TEXT, samplingtimestamp TEXT, amrgenes TEXT, virulencegenes TEXT, plasmids TEXT, consensus_name TEXT, referenceid TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS referencetable(entryid TEXT PRIMARY KEY, amrgenes TEXT, virulencegenes TEXT, plasmids TEXT, header_text TEXT)""") #Mangler finder results. Implement eventually
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS specietable(specie TEXT PRIMARY KEY, entryid TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS amrtable(entryid TEXT PRIMARY KEY, samplename TEXT, analysistimestamp TEXT, amrgenes TEXT, phenotypes TEXT, specie TEXT, risklevel TEXT, warning TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS metadatatable(entryid TEXT PRIMARY KEY, {})""".format(metadata_string))
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS ipctable(ipc TEXT PRIMARY KEY, ipc_index_refdb TEXT, IsolateJSON TEXT, ReferenceJSON TEXT, ReadRefDB TEXT, running_analyses TEXT, queued_analyses TEXT, finished_analyses TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS statustable(entryid TEXT PRIMARY KEY, status TEXT, type TEXT, current_stage TEXT, final_stage TEXT, result TEXT, time_stamp TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS local_sync_table(entryid TEXT PRIMARY KEY, time_of_analysis TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS basecalling_table(name TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT)""")
conn.commit()
dbstring = "INSERT INTO ipctable(ipc, ipc_index_refdb, ReadRefDB, running_analyses, queued_analyses, finished_analyses) VALUES('{}' ,'{}', '{}', '{}', '{}', '{}')".format('IPC',1, 100, "", "", "")
c.execute(dbstring)
conn.commit()
conn.close()
#Can we add tables for genes with pointers? Better solution!


moss.init_insert_reference_table(configname)

# Generate config.json file
jsondict = dict()
jsondict["current_working_db"] = args.configname
with open("/opt/moss_db/config.json", 'w') as f_out:
  json.dump(jsondict, f_out)
f_out.close()

cmd = "python3 /opt/moss/src/createGuppyWorkflowDict.py -current_working_db {}".format(args.configname)
os.system(cmd)