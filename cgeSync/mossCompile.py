# Copyright (c) 2021, Malte Hallgren Technical University of Denmark
# All rights reserved.
#
#Status: pause pt. fix cge

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

def databaseOverClustering(moss_path, kma_path, filename):
    cmd = "{} dist -t_db {}update/database/tmp/homologyReducedDB.ATG -d 1 -o {}update/database/tmp/referencecluster".format(kma_path, moss_path, moss_path)
    os.system(cmd)
    distancematrix = []
    infile = open("{}update/database/tmp/referencecluster".format(moss_path), 'r')
    for line in infile:
        line = line.rstrip().split("\t")
        distancematrix.append(line)
    infile.close()
    threshhold = 1000
    clustercount = 0
    writefile = open(filename, 'w')
    for i in range(2,len(distancematrix), 1): #Skip matrixsizeline and first reference line, which has no value #Row
        for t in range(0, len(distancematrix[i])-1, 1): #Collum
            if (threshhold > int(distancematrix[i][t+1])):
                print("{}\t{}\t{}".format(distancematrix[i][0], distancematrix[i][t+1], distancematrix[t+1][0]), file=writefile)
                clustercount += 1
    print (clustercount)
    writefile.close()
    return clustercount



#Script

moss_path = "/home/people/malhal/MOSS/" #Change to argparse input
kma_path = "/home/data1/services/MINTyper/MINTyper-1.0/scripts/bin/MINTyper/kma/kma" #Change to argparse input

#Check nameclashes

unique_reference_list = []
reference_path_list = []

#Copy unique referencenames
user_list = os.listdir(moss_path + "current/")

for username in user_list:
    referencenames = os.listdir(moss_path + "current/" + username + "/referenceCons/")
    for referencename in referencenames:
        if referencename not in user_list:
            unique_reference_list.append(referencename)
            reference_path_list.append(moss_path + "current/" + username + "/referenceCons/" + referencename)
        else:
            print ("Two references with same name were found, IMPLEMENT SOLUTION")

reference_string = " ".join(reference_path_list)

for i in range(len(reference_path_list)):
    cmd = "cp {} {}/update/referenceCons/.".format(reference_path_list[i], moss_path)
    os.system(cmd)

cmd = "{} index -i {}/update/referenceCons/* -Sparse ATG -o {}update/database/tmp/homologyReducedDB.ATG".format(kma_path, moss_path, moss_path)
os.system(cmd)

clusternumber = databaseOverClustering(moss_path, kma_path, moss_path + "update/database/tmp/clusterreport")
os.system(cmd)

#sys.exit("Check clusterreport")

if clusternumber > 0:
    killList = []
    infile = open(moss_path + "update/database/tmp/clusterreport", 'r')
    for line in infile:
        line = line.rstrip().split("\t")
        if line[2] not in killList:
            killList.append(line[2])
    infile.close()

    print ("starting homology reduction")
    cmd = "{} seq2fasta -t_db {}update/database/tmp/homologyReducedDB.ATG > {}update/database/tmp/homored.fasta".format(kma_path, moss_path, moss_path)
    os.system(cmd)

    infile = open(moss_path + "update/database/tmp/homoredREFDB.fasta", 'r')
    outfile = open(moss_path + "update/database/tmp/reduceddb.fasta", 'w')
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
    infile.close() #This only removes clashes, does not resort them! #Identify removals and reindex as isolates
    outfile.close()

    cmd = "{} index -i {}update/database/tmp/reduceddb.fasta -Sparse ATG -o {}update/database/homored/homologyReducedDB.ATG".format(kma_path, moss_path, moss_path)
    os.system(cmd)

    #Inklude killlist som nye isolater - kør nu analyse

    

    #Cleaning
    #cmd = "rm {}homoredREFDB.fasta".format(moss_path)
    #os.system(cmd)
    #cmd = "rm {}reduceddb.fasta".format(moss_path)
    #os.system(cmd)
    #cmd = "rm {}clusterreport".format(moss_path)
    #os.system(cmd)
    #cmd = "rm {}referenceCluster".format(moss_path)
    #os.system(cmd)


    #WIPE ALL EXPECT STABLE
    
    

elif clusternumber == 0:
    print ("No clashing references were found")

