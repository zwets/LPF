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

target_dir = "/home/malte/testdir/mosstest/nt2/analysis/7dc39a287651450d2514da0ea694552f/"
entryid = "7dc39a287651450d2514da0ea694552f"
db_dir = "/home/malte/testdir/mosstest/nt2/"
image_location = "/home/malte/testdir/mosstest/nt2//datafiles/distancematrices/NZ_CP024801.1/tree.png"
templatename = "NZ_CP024801.1 Escherichia coli strain AMA1167 chromosome, complete genome"
distance = "0.0"



moss.compileReportAlignment("ID:", target_dir, entryid, db_dir, image_location, templatename,
                            distance)  # No report compiled for assemblies! Look into it! #TBD
