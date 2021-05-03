# Copyright (c) 2019, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries


import sys
import os
import argparse
import operator
import time
import gc
import numpy as np
import array
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-inputfiles_files_path', action="store", type=str, dest='files_path', default="", help='Path to your DB-directory')
args = parser.parse_args()

input_files = os.listdir(args.files_path)
input_files.sort()
complete_path_files = []
for i in range(len(input_files)):
    complete_path_files.append(args.files_path + input_files[i])

new_complete_list = []
for i in range(0,len(complete_path_files), 2):
    new_complete_list.append(complete_path_files[i])


##cmd = "MinION-Typer surveillance -i_illumina /home/maha/12STA_Illumina/CPO20180100_S79_L555_R1_001.fastq.gz -ref_kma_db /home/maha/dbtest/refdb/KMADB.ATG -dcmMethylation N -prune -prune_distance 10 -thread 5 -isolate_db /home/maha/dbtest/refdb/MinION-Typer.db -reference_storage /home/maha/dbtest/refdb/references/ -o kmaref10"
#cmd = "MinION-Typer surveillance -i_illumina {} -ref_kma_db /home/maha/dbtest/refdb/KMADB.ATG -dcmMethylation N -prune -prune_distance 10 -thread 5 -isolate_db /home/maha/dbtest/refdb/MinION-Typer.db -reference_storage /home/maha/dbtest/refdb/references/ -o kmaref{}".format(complete_path_files[i], str(i))
#os.system(cmd)

for i in range(len(new_complete_list)):
    cmd = "MinION-Typer surveillance -i_illumina {} -ref_kma_db /home/maha/tests/dbtest/KMADB.ATG -dcmMethylation N -prune -prune_distance 10 -thread 5 -isolate_db /home/maha/tests/dbtest/MinION-Typer.db -reference_storage /home/maha/tests/dbtest/references/ -o kmaref{}".format(new_complete_list[i], str(i))
    os.system(cmd)

MinION-Typer2 surveillance -i_illumina /home/maha/CPO/illumina/raw_illumina/CPO20140039_S7_L001_R1_001.fastq.gz -ref_kma_db /home/maha/tests/non_spars_90_test/KMADB.ATG -dcmMethylation N -prune -prune_distance 10 -thread 5 -isolate_db /home/maha/tests/non_spars_90_test/MinION-Typer.db -reference_storage /home/maha/tests/non_spars_90_test/references/ -o newtesttttt