import sys
import os
import argparse
import operator
import time
import geocoder
import gc
import numpy as np
import array
import subprocess
import threading
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3
import json
import datetime
import hashlib
import gzip

import pandas as pd
from tabulate import tabulate
from IPython.display import display, HTML
import gzip
from fpdf import FPDF
from pandas.plotting import table
from geopy.geocoders import Nominatim
from subprocess import check_output, STDOUT

import moss_functions as moss
import matplotlib
import matplotlib.pyplot as plt
from Bio import Phylo
from io import StringIO
import pylab
import dataframe_image as dfi


parser = argparse.ArgumentParser(description='.')
parser.add_argument("-config_name", action="store", default = False, dest="config_name", help="config_name")
args = parser.parse_args()

class Object(object):
    pass

def local_sync(args):
    sync_object = Object()
    isolatedb = "/opt/moss_db/{}/moss.db".format(args.config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    last_sync = moss.sql_fetch_one("SELECT last_sync FROM sync_table", args.config_name)[0]
    hits = moss.sql_fetch_all("SELECT entry_id FROM status_table WHERE time_stamp>'{}' AND status='Completed'".format(last_sync), args.config_name)
    conn.close()
    for item in hits:
        sync_object.item = fetch_data_from_id(item)
    dump(sync_object)

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def fetch_data_from_id(id):
    isolatedb = "/opt/moss_db/{}/moss.db".format(args.config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    isolate_object = Object()
    isolate_object.sample_name = moss.sql_fetch_one("SELECT sample_name FROM sample_table WHERE entry_id = '{}'".format(id), args.config_name)[0]
    isolate_object.amr_genes = moss.sql_fetch_one("SELECT amr_genes FROM sample_table WHERE entry_id = '{}'".format(id), args.config_name)[0]
    isolate_object.virulence_genes = moss.sql_fetch_one("SELECT virulence_genes FROM sample_table WHERE entry_id = '{}'".format(id), args.config_name)[0]
    isolate_object.plasmids = moss.sql_fetch_one("SELECT plasmids FROM sample_table WHERE entry_id = '{}'".format(id), args.config_name)[0]
    isolate_object.consensus_name = moss.sql_fetch_one("SELECT consensus_name FROM sample_table WHERE entry_id = '{}'".format(id), args.config_name)[0]
    conn.close()

    return isolate_object

def main():
    local_sync(args)


if __name__== "__main__":
  main()
