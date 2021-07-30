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


#Give path to database directory
#Give initial files for references
#Give directories with isolates corresponing to references
#In database directory make two directories, one for KMA DB and one for MIONT-DB
#PRUNE CURRENTLY NOT INPLEMENTED!!!


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-kmaindex_db_path', action="store", type=str, dest='kmaindex_db_path', default="", help='Path a .ATG kma-index database that is desired to be used a references. It is expected that both the .ATG.name file and .ATG.seq.b file is present in this directory, and that NO OTHER files are present. http://www.cbs.dtu.dk/public/CGE/databases/KmerFinder/version/20190108_stable/ link to bacteria.tar.gz, which is a good option for a starting database')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')
parser.add_argument("-exepath", action="store", dest="exepath", default = "", help="Complete path to the moss repo that you cloned, in which your kma and ccphylo folder at located.")
parser.add_argument("-syncpath", action="store", dest="syncpath", default = "", help="Complete path to MOSS directory at remote server.")
parser.add_argument("-configname", action="store", dest="configname", help="Enter a name for your configuration file.")

args = parser.parse_args()

kma_path = args.exepath + "kma/kma"

kmaindex_db_path = moss.correctPathCheck(args.kmaindex_db_path)
db_dir = moss.correctPathCheck(args.db_dir)
exepath = moss.correctPathCheck(args.exepath)
syncpath = moss.correctPathCheck(args.syncpath)
if kmaindex_db_path != "":
    try:
        os.makedirs(db_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print ("dbdir already exists")
            raise

    # Generate localDBAddition.json
    referenceadditionjsondict = dict()

    print ("cloning reference DB, if you are using a big reference DB, this might take a while")
    filename = os.listdir(kmaindex_db_path)[0].split(".")[0]
    cmd = "cp {}*.ATG.comp.b {}REFDB.ATG.comp.b".format(kmaindex_db_path, db_dir)
    os.system(cmd)
    cmd = "cp {}*.ATG.length.b {}REFDB.ATG.length.b".format(kmaindex_db_path, db_dir)
    os.system(cmd)
    cmd = "cp {}*.ATG.seq.b {}REFDB.ATG.seq.b".format(kmaindex_db_path, db_dir)
    os.system(cmd)
    cmd = "cp {}*.ATG.name {}REFDB.ATG.name".format(kmaindex_db_path, db_dir)
    os.system(cmd)
    print ("cloning reference DB complete")

    cmd = "mkdir " + db_dir + "analyticalFiles"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "analysis"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "datafiles"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "datafiles/isolatefiles"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "datafiles/distancematrices"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "multiSampleAnalysisReports"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "syncFiles"
    os.system(cmd)

    cmd = "mkdir " + db_dir + "preliminaryEstimations"
    os.system(cmd)

    # Create update log file:
    # Initialize isolate sync
    updatejson = dict()
    updatejson['updateTime'] = "None"
    updatejson['updateID'] = "None"
    with open("{}syncFiles/update.log".format(args.db_dir), 'w') as f_out:
        json.dump(updatejson, f_out)
    f_out.close()

    # Create runningAnalyses.json
    analysesdict = dict()
    with open("{}analyticalFiles/runningAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(analysesdict, f_out)
    f_out.close()

    # Create finishedAnalyses.json
    analysesdict = dict()
    with open("{}analyticalFiles/finishedAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(analysesdict, f_out)
    f_out.close()

    # Create queuedAnalysis.json
    analysesdict = dict()
    with open("{}analyticalFiles/queuedAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(analysesdict, f_out)
    f_out.close()


    infile = open("{}REFDB.ATG.name".format(db_dir), 'r')
    linenumber = 1
    headerlist = []
    referencelist = []
    for line in infile:
        line = line.rstrip()
        template_id = linenumber
        header = line
        if " " in header:  # Assumes a standard header begining with a accession ID
            accession = header.split(" ")[0]
        else:
            accession = header
        cmd = "mkdir " + db_dir + "datafiles/isolatefiles/\"{}\"".format(accession)
        os.system(cmd)
        cmd = "mkdir " + db_dir + "datafiles/distancematrices/\"{}\"".format(accession)
        os.system(cmd)
        referenceadditionjsondict[accession] = {'headerid': header, 'filename': accession}
        cmd = "{} seq2fasta -t_db {}REFDB.ATG -seqs {} > {}datafiles/isolatefiles/{}/{}".format(kma_path, db_dir, str(template_id), db_dir, accession, accession)
        os.system(cmd)
        headerlist.append(header)
        referencelist.append(accession)
        linenumber += 1
    infile.close()

    conn = sqlite3.connect(db_dir + 'moss.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS isolatetable(entryid TEXT PRIMARY KEY, headerid TEXT, isolatename TEXT, timestamp TEXT, amrgenes TEXT, virulencegenes TEXT, plasmids TEXT)""")
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS referencetable(entryid TEXT PRIMARY KEY, headerid TEXT, refname TEXT, isolateid TEXT, timestamp TEXT, amrgenes TEXT, virulencegenes TEXT, plasmids TEXT)""") #Mangler finder results. Implement eventually
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS specietable(specie TEXT PRIMARY KEY, entryid TEXT)""")
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS amrtable(entryid TEXT PRIMARY KEY, isolatename TEXT, timestamp TEXT, amrgenes TEXT, phenotypes TEXT, specie TEXT, risklevel TEXT, warning TEXT)""")
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS metadatatable(entryid TEXT PRIMARY KEY, diseases TEXT, location TEXT, patientID TEXT, amrgenes TEXT, riskscore TEXT)""")
    conn.commit()

    for i in range(len(referencelist)):
        entryid = moss.md5("{}datafiles/isolatefiles/{}/{}".format(db_dir, referencelist[i], referencelist[i]))
        headerid = headerlist[i]
        if "'" in headerid:
            headerid = headerid.replace("'", "''")
            print (headerid)
        accession = referencelist[i]
        dbstring = "INSERT INTO referencetable(entryid, headerid, refname) VALUES('{}', '{}', '{}')".format(entryid, headerid, accession)
        c.execute(dbstring)
        referenceadditionjsondict[accession].update({'entryid': entryid})
    conn.commit()
    conn.close()


    # Generate config.json file
    jsondict = dict()
    jsondict["dbdir"] = db_dir
    jsondict["exepath"] = exepath
    jsondict["syncpath"] = syncpath
    with open("{}{}_moss_config.json".format(db_dir, args.configname), 'w') as f_out:
      json.dump(jsondict, f_out)
    f_out.close()

    # Generate localDBAddition.json
    referenceadditionjsondict['timestamp'] = str(time.time())
    with open("{}syncFiles/referenceSync.json".format(db_dir), 'w') as f_out:
        json.dump(referenceadditionjsondict, f_out)
    f_out.close()

    # Initialize isolate sync
    isolateadditionjson = dict()
    isolateadditionjson['timestamp'] = str(time.time())
    with open("{}syncFiles/isolateSync.json".format(db_dir), 'w') as f_out:
        json.dump(isolateadditionjson, f_out)
    f_out.close()