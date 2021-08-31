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

target_dir = "/home/malte/testdir/mosstest/nt3/analysis/55d9edce6f78366a0de75c0c4042ae3b/"
entryid = "55d9edce6f78366a0de75c0c4042ae3b"
db_dir = "/home/malte/testdir/mosstest/nt3/"
image_location = "/home/malte/testdir/mosstest/nt3/datafiles/distancematrices/NZ_CP024801.1/tree.png"
templatename = "NZ_CP024801.1 Escherichia coli strain AMA1167 chromosome, complete genome"
exepath = "/home/malte/dev/tmp/MicrobialOutbreakSurveillanceSystem1/"



moss.compileReportAlignment("ID:", target_dir, entryid, db_dir, image_location, templatename, exepath)  # No report compiled for assemblies! Look into it! #TBD
