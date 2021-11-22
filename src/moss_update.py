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
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='exepath')
parser.add_argument("-mac", action="store_true", dest="mac", default = False, help="Mac.")
parser.add_argument("-force", action="store_true", dest="force", default = False, help="force.")

args = parser.parse_args()

exepath = moss.correctPathCheck(args.exepath)
force = args.force
mac = args.mac

if force:
    moss.update_moss_dependencies(exepath, mac, [], True)
else:
    update_list = moss.varify_all_dependencies(exepath, mac)
    moss.update_moss_dependencies(exepath, mac, update_list, False)

