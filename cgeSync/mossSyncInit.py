# Copyright (c) 2021, Malte Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries

import sys
import os
import argparse
import operator
import time
import gc
#import numpy as np
import array
import subprocess
from optparse import OptionParser
from operator import itemgetter
import re
import json

#Assume mossdir in created and current dir

cmd = "mkdir current"
os.system(cmd)

cmd = "mkdir stable"
os.system(cmd)

cmd = "mkdir update"
os.system(cmd)

cmd = "mkdir current/malhal" #Change to username
os.system(cmd)

cmd = "mkdir current/malhal/isolateCons" #Change to username
os.system(cmd)

cmd = "mkdir current/malhal/isolateSync" #Change to username
os.system(cmd)

cmd = "mkdir current/malhal/referenceCons" #Change to username
os.system(cmd)

cmd = "mkdir current/malhal/referenceSync" #Change to username
os.system(cmd)

cmd = "mkdir update/referenceCons"
os.system(cmd)

cmd = "mkdir update/database"
os.system(cmd)

cmd = "mkdir update/database/tmp"
os.system(cmd)

cmd = "mkdir update/database/homored"
os.system(cmd)

