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
def local_sync(args):
    isolatedb = "/opt/moss_db/{}/moss.db".format(args.config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    last_sync = moss.sql_fetch_one("SELECT last_sync FROM sync_table", args.config_name)[0]
    print ("SELECT entry_id FROM sample_table WHERE time_stamp>{}".format(last_sync))
    hits = moss.sql_fetch_all("SELECT entry_id FROM sample_table WHERE time_stamp>{}".format(last_sync), args.config_name)
    sys.exit(hits)

    conn.close()

def main():
    local_sync(args)


if __name__== "__main__":
  main()
