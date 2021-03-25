#In case your computer shuts down midway through a process, and your semaphore are not closed correctly, run this script to reset all semaphores!
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
semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100)
assembly_semaphore_value = semaphore.value
print (assembly_semaphore_value)
semaphore.unlink()
semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
assembly_semaphore_value = semaphore.value
print (assembly_semaphore_value)
semaphore.unlink()
semaphore = posix_ipc.Semaphore("/IsolateJSON", posix_ipc.O_CREAT, initial_value=1)
assembly_semaphore_value = semaphore.value
print (assembly_semaphore_value)
semaphore.unlink()
semaphore = posix_ipc.Semaphore("/ReferenceJSON", posix_ipc.O_CREAT, initial_value=1)
assembly_semaphore_value = semaphore.value
print (assembly_semaphore_value)
semaphore.unlink()
