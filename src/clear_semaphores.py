# Copyright (c) 2019, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries
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

import moss_sql as moss_sql
from Bio import Phylo
import matplotlib.pyplot as plt
import pylab
import dataframe_image as dfi

config_name = "test1"

print(moss.check_sql_semaphore_value( "ipc_index_refdb", config_name))

moss.reset_semaphore("ipc_index_refdb", config_name)

print(moss.check_sql_semaphore_value( "ipc_index_refdb", config_name))