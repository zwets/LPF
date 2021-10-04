import sys
import os
import argparse
import operator
import random
import subprocess
import time
import gc
import numpy as np
import array
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3
import moss_functions as moss
import json
import datetime
import threading
import posix_ipc

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='db_dir')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='db_dir')

args = parser.parse_args()

db_dir = args.db_dir
exepath = args.exepath

onlyfiles = [f for f in os.listdir(db_dir + "/analysis/") if os.path.isdir(os.path.join(db_dir + "/analysis/", f))]
for file in onlyfiles:
    logfile = db_dir + "/analysis/" + file + "/logf*"

    cmd = "grep \"Best template: \" {}".format(logfile)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()
    refname = id.split()[2]
    templatename = id.split()[2:]
    templatename = " ".join(templatename)

    entryid = file
    target_dir = db_dir + "analysis/" + entryid + "/"
    logfile = db_dir + "/analysis/" + file + "/logf*"
    inputdir = "{}/datafiles/distancematrices/{}/".format(db_dir, refname)
    image_location = "{}tree.png".format(inputdir)
    target_dir = db_dir + "analysis/"
    cmd = "grep \"mpr:\" {}".format(logfile)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()
    print (id)
    result = id.split()[-1]

    associated_species = "No related reference identified, required manual curation. ID: {} name: {}".format(entryid,
                                                                                                             file)

    if result == 'true':
        moss.compileReportAlignment(target_dir, entryid, db_dir, image_location, templatename, exepath)  # No report compiled for assemblies! Look into it! #TBD
    elif result == 'false':
        moss.compileReportAssembly(target_dir, entryid, db_dir, image_location, associated_species, exepath)

#value = moss.check_sql_semaphore_value(db_dir, 'IndexRefDB')
#moss.compileReportAlignment(target_dir, entryid, db_dir, image_location, templatename, exepath)  # No report compiled for assemblies! Look into it! #TBD
#moss.compileReportAssembly(target_dir, entryid, db_dir, image_location, associated_species, exepath)