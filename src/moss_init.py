"""
Script for initializing a MOSS database system from a KMA-indexed reference database.
"""

import sys
import os
import argparse
import moss_functions as moss
import datetime
import json
import sqlite3
from pathlib import Path

def check_and_add_bookmarks(config_name):
    home = str(Path.home())
    if os.path.exists("{}/.config/gtk-3.0/bookmarks".format(home)):
        with open("{}/.config/gtk-3.0/bookmarks".format(home)) as fd:
            data = fd.readlines()
        new_bookmark_list = list()
        for item in data:
            if "moss" not in item:
                new_bookmark_list.append(item.rstrip())
        new_bookmark_list.append("file:///opt/moss_data")
        new_bookmark_list.append("file:///opt/moss_db/{}/metadata_csv".format(config_name))

        with open("{}/.config/gtk-3.0/bookmarks".format(home), 'w') as fd:
            for item in new_bookmark_list:
                fd.write(item + '\n')


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-kmaindex_db_path', action="store", type=str, dest='kmaindex_db_path', default="", help='Path a .ATG kma-index database that is desired to be used a references. It is expected that both the .ATG.name file and .ATG.seq.b file is present in this directory, and that NO OTHER files are present. http://www.cbs.dtu.dk/public/CGE/databases/KmerFinder/version/20190108_stable/ link to bacteria.tar.gz, which is a good option for a starting database')
parser.add_argument("-config_name", action="store", dest="config_name", help="Enter a name for your configuration file.")

args = parser.parse_args()

kma_path = "/opt/moss/kma/kma"
config_name = args.config_name

check_and_add_bookmarks(config_name)

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
with open("/opt/moss/datafiles/ena_list.json") as json_file:
    data = json.load(json_file)
for item in data:
    if '\ufeff' in item:
        item = item.replace(u'\ufeff', '')
    metadata_string += "{} TEXT,".format(item)
metadata_string = metadata_string[:-1]

c.execute("""CREATE TABLE IF NOT EXISTS sample_table(entry_id TEXT PRIMARY KEY, sample_name TEXT, reference_id TEXT, amr_genes TEXT, virulence_genes TEXT, plasmids TEXT, consensus_name TEXT, mlst TEXT)""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS reference_table(entry_id TEXT PRIMARY KEY, reference_header_text TEXT)""") #Mangler finder results. Implement eventually
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS metadata_table(entry_id TEXT PRIMARY KEY, {})""".format(metadata_string))
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS status_table(entry_id TEXT PRIMARY KEY, sample_name TEXT, status TEXT, type TEXT, current_stage TEXT, final_stage TEXT, result TEXT, time_stamp TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS sync_table(last_sync TEXT, sync_round TEXT)""")
conn.commit()
c.execute( """CREATE TABLE IF NOT EXISTS basecalling_table(name TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT)""")
conn.commit()
dbstring = "INSERT INTO sync_table(last_sync) VALUES('{}')".format(str(datetime.datetime.now())[0:-7])
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

# Generate config.json file
jsondict = dict()
jsondict["current_working_db"] = args.config_name
with open("{}/sync_files/local_changes.json".format(config_name), 'w') as f_out:
  json.dump(jsondict, f_out)
f_out.close()

sys.exit(0) #GH action