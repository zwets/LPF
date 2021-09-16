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

target_dir = "/home/malte/testdir/mosstest/nt1/analysis/4a6969f363a074488ae75c99a1640bec/"
entryid = "4a6969f363a074488ae75c99a1640bec"
db_dir = "/Users/malhal/mosstest/nt1/"
image_location = "/home/malte/testdir/mosstest/nt1/datafiles/distancematrices/NZ_CP024801.1/tree.png"
templatename = "NZ_CP024801.1 Escherichia coli strain AMA1167 chromosome, complete genome"
associated_species = "Escherichia coli something something"
exepath = "/home/malte/dev/tmp/MicrobialOutbreakSurveillanceSystem1/"



result, action = moss.homemade_semaphore('IndexRefDB', db_dir, 1, 45)



#value = moss.check_sql_semaphore_value(db_dir, 'IndexRefDB')
#moss.compileReportAlignment(target_dir, entryid, db_dir, image_location, templatename, exepath)  # No report compiled for assemblies! Look into it! #TBD
#moss.compileReportAssembly(target_dir, entryid, db_dir, image_location, associated_species, exepath)