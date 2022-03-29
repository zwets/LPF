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
import subprocess
from optparse import OptionParser
from operator import itemgetter
import moss_functions as moss
import re
import json
import sqlite3
import collections

#Note: Homology reducing the databse requires a lot of RAM.


parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-configname', action="store", type=str, dest='configname', default="", help='Path the directory with your database')
parser.add_argument('-databasename', action="store", type=str, dest='dbname', default="", help='Path the directory with your database')
parser.add_argument('-exepath', action="store", type=str, dest='exepath', default="", help='Path to your DB-directory')


args = parser.parse_args()

#Load previous file, needs to be done
configname = moss.correctPathCheck(args.configname)
exepath = moss.correctPathCheck(args.exepath)

kma_path = exepath + "kma/kma"


clusternumber = moss.databaseOverClustering(configname, args.dbname, kma_path, configname + "clusterreport")

if clusternumber > 0:
    killList = []
    uniquelist = []
    infile = open(configname + "clusterreport", 'r')
    for line in infile:
        line = line.rstrip().split("\t")
        if line[2] not in killList: #Append all non init names
            killList.append(line[2])
    infile.close()

    print ("starting homology reduction")
    cmd = "{} seq2fasta -t_db {}{} > {}homoredREFDB.fasta".format(kma_path, configname, args.dbname, configname)
    os.system(cmd)

    infile = open(configname + "homoredREFDB.fasta", 'r')
    outfile = open(configname + "reduceddb.fasta", 'w')
    printflag = False
    for line in infile:
        line = line.rstrip()
        if printflag == True:
            print (line, file=outfile)
            printflag = False
        if line[0] == ">":
            if line[1:] not in killList:
                print (line, file=outfile) #Header
                printflag = True
    infile.close()
    outfile.close()

    cmd = "{} index -i {}reduceddb.fasta -Sparse ATG -o {}homologyReducedDB.ATG".format(kma_path, configname, configname)
    os.system(cmd)

    #Cleaning
    cmd = "rm {}homoredREFDB.fasta".format(configname)
    os.system(cmd)
    cmd = "rm {}reduceddb.fasta".format(configname)
    os.system(cmd)
    cmd = "rm {}clusterreport".format(configname)
    os.system(cmd)
    cmd = "rm {}referenceCluster".format(configname)
    os.system(cmd)




