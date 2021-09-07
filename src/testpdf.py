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

target_dir = "/home/malte/testdir/mosstest/nt1/analysis/72dd88b419a634ec250f4ae8c56182da/"
entryid = "72dd88b419a634ec250f4ae8c56182da"
db_dir = "/home/malte/testdir/mosstest/nt1/"
image_location = "/home/malte/testdir/mosstest/nt1/datafiles/distancematrices/NZ_CP024801.1/tree.png"
templatename = "NZ_CP024801.1 Escherichia coli strain AMA1167 chromosome, complete genome"
associated_species = "Escherichia coli something something"
exepath = "/home/malte/dev/tmp/MicrobialOutbreakSurveillanceSystem1/"



moss.compileReportAlignment(target_dir, entryid, db_dir, image_location, templatename, exepath)  # No report compiled for assemblies! Look into it! #TBD
#moss.compileReportAssembly(target_dir, entryid, db_dir, image_location, associated_species, exepath)