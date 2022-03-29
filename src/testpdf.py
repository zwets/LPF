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


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='configname')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='configname')

args = parser.parse_args()

configname = args.configname
exepath = args.exepath

onlyfiles = [f for f in os.listdir(configname + "/analysis/") if os.path.isdir(os.path.join(configname + "/analysis/", f))]
for file in onlyfiles:
    logfile = configname + "/analysis/" + file + "/logf*"

    cmd = "grep \"Best template: \" {}".format(logfile)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()
    header_text = id.split()[2]
    header_text = id.split()[2:]
    header_text = " ".join(header_text)

    entryid = file
    target_dir = configname + "analysis/" + entryid + "/"
    logfile = configname + "/analysis/" + file + "/logf*"
    inputdir = "{}/datafiles/distancematrices/{}/".format(configname, header_text)
    image_location = "{}tree.png".format(inputdir)
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
        moss.compileReportAlignment(target_dir, entryid, configname, image_location, header_text, exepath)  # No report compiled for assemblies! Look into it! #TBD
    elif result == 'false':
        moss.compileReportAssembly(target_dir, entryid, configname, associated_species, exepath)

#value = moss.check_sql_semaphore_value(configname, 'ipc_index_refdb')
#moss.compileReportAlignment(target_dir, entryid, configname, image_location, header_text, exepath)  # No report compiled for assemblies! Look into it! #TBD
#moss.compileReportAssembly(target_dir, entryid, configname, image_location, associated_species, exepath)