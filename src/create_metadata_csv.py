#!/usr/bin/env python3

# WS client example

import sys
import os
import argparse
import operator
import time
import json
import sqlite3
import moss_functions as moss


parser = argparse.ArgumentParser(description='create_metadata_csv')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='comma-seperated names')
parser.add_argument('-input_type', action="store", type=str, dest='input_type', default="", help='input type')
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='configname for moss directory')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='exepath')
parser.add_argument('-name', action="store", type=str, dest='name', default="", help='name')
args = parser.parse_args()

input = args.input
if args.name[-3:] == "csv":
    name = args.name
else:
    name = args.name + ".csv"
if ";" in args.input:
    input = input.split(";")
elif "," in args.input:
    input = input.split(",")
else:
    input = input.split()
name_list = []
if args.input_type == "pe":
    if len(input)%2 != 0:
        sys.exit("An uneven number of input files was given, and the sequence type was given as paired end.")
    for i in range(0,len(input), 2):
        name_list.append(input[i] + " " + input[i+1])
else:
    name_list = input

if os.path.isfile('{}static_files/metadata_csv/{}'.format(args.configname, name)):
    sys.exit('A metadata file with this name already exists'.upper())
else:
    cmd = "cp {}datafiles/ENA_list.csv {}static_files/metadata_csv/{}".format(args.exepath, args.configname, name)
    os.system(cmd)

with open('{}static_files/metadata_csv/{}'.format(args.configname, name)) as f:
    header = f.readline()
empty_line = len(header.split(","))*","


outfile = open("{}static_files/metadata_csv/{}".format(args.configname, name), 'w')
print (header, file = outfile)
for item in name_list:
    print_line = item + empty_line
    print (print_line, file=outfile)
outfile.close()



