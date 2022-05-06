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
parser.add_argument('-config_name', action="store", type=str, dest='config_name', default="", help='config_name')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='config_name')

args = parser.parse_args()

config_name = args.config_name
exepath = args.exepath

onlyfiles = [f for f in os.listdir(config_name + "/analysis/") if os.path.isdir(os.path.join(config_name + "/analysis/", f))]
for file in onlyfiles:
    logfile = config_name + "/analysis/" + file + "/logf*"

    cmd = "grep \"Best template: \" {}".format(logfile)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()
    reference_header_text = id.split()[2]
    reference_header_text = id.split()[2:]
    reference_header_text = " ".join(reference_header_text)

    entry_id = file
    target_dir = config_name + "analysis/" + entry_id + "/"
    logfile = config_name + "/analysis/" + file + "/logf*"
    inputdir = "{}/datafiles/distancematrices/{}/".format(config_name, reference_header_text)
    image_location = "{}tree.png".format(inputdir)
    cmd = "grep \"mpr:\" {}".format(logfile)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()
    print (id)
    result = id.split()[-1]

    associated_species = "No related reference identified, required manual curation. ID: {} name: {}".format(entry_id,
                                                                                                             file)

    if result == 'true':
        moss.compileReportAlignment(target_dir, entry_id, config_name, image_location, reference_header_text, exepath)  # No report compiled for assemblies! Look into it! #TBD
    elif result == 'false':
        moss.compileReportAssembly(target_dir, entry_id, config_name, associated_species, exepath)

#value = moss.check_sql_semaphore_value(config_name, 'ipc_index_refdb')
#moss.compileReportAlignment(target_dir, entry_id, config_name, image_location, reference_header_text, exepath)  # No report compiled for assemblies! Look into it! #TBD
#moss.compileReportAssembly(target_dir, entry_id, config_name, image_location, associated_species, exepath)