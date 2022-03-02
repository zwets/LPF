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
import datetime



parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-reference', action="store", type=str, dest='reference', default="", help='Accesion ID of the reference you wish to do an association analysis of')
parser.add_argument('-as', action="store", type=int, default=1, dest='association_size', help='Maximum number of nearby clusters you wish to include. Nearby clusters will only be included, if the cluster is within 3000 basepairs')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='Path to your DB-directory')
parser.add_argument("-exepath", action="store", dest="exepath", default = "", help="Complete path to the moss repo that you cloned, in which your kma and ccphylo folder at located.")
parser.add_argument("-nonewcluster", action="store_false", dest="newcluster", default = True, help="Use this flag, if you DO NOT wish to calculate a new reference cluster")
parser.add_argument("-o", action="store", dest="output", help="Name that you would like the output directory to be called.")

args = parser.parse_args()

start_time = datetime.datetime.now()

kma_path = args.exepath + "kma/kma"
ccphylo_path = args.exepath + "ccphylo/ccphylo"

db_dir = moss.correctPathCheck(args.db_dir)
exepath = moss.correctPathCheck(args.exepath)

if args.newcluster == True:
    cmd = "{} dist -t_db {}{} -d 1 -o {}datafiles/referenceCluster -tmp {}".format(kma_path, db_dir, "REFDB.ATG", db_dir, db_dir)
    os.system(cmd)

infile = open("{}/datafiles/referenceCluster".format(db_dir), 'r')
distancematrix = []
referenceposition = ""
linecount = 0
for line in infile:
    line = line.rstrip().split("\t")
    name = line[0]
    ID = line[0].split(" ")[0]
    if name == args.reference or ID == args.reference:
        referenceposition = linecount
    distancematrix.append(line)
    linecount += 1
infile.close()

refnumber = linecount - 1

if referenceposition == "":
    sys.exit("No reference with the given ID was found")



positiondict = dict()
refvector = distancematrix[referenceposition]


for i in range(referenceposition+1, refnumber, 1): #aDD remaining half of distances
    refvector.append(distancematrix[i][referenceposition])

for i in range(len(refvector)):
    positiondict[i+1] = refvector[i]

sortedposdict = dict(sorted(positiondict.items(), key=lambda item: item[1]))





confirmedAssociates = []

assonumber = args.association_size
addedclusters = 0

isolatedb = args.db_dir + "moss.db"

conn = sqlite3.connect(isolatedb)
c = conn.cursor()

c.execute("SELECT * FROM referencetable WHERE isolateid != ''")
referencelist = c.fetchall()

conn.close()

refheaders = []
for i in range(len(referencelist)): #Non empty clusters
    refheaders.append(referencelist[i][1])

for i in range(len(sortedposdict)):
    position = int(list(sortedposdict.keys())[i])
    if distancematrix[position][0] in refheaders:
        if position > referenceposition:
            if int(distancematrix[position][referenceposition]) < 10000: #### HUSK AT JUSTER! MÅSKE 10k, eller user parameter??
                print ("sucess")
                confirmedAssociates.append(distancematrix[position][0])
                print (distancematrix[position][0])
                addedclusters += 1
        elif position < referenceposition:
            if int(distancematrix[referenceposition][position]) < 10000: #### HUSK AT JUSTER! MÅSKE 10k, eller user parameter??
                print ("sucess")
                confirmedAssociates.append(distancematrix[position][0])
                print (distancematrix[position][0])
                addedclusters += 1
    if addedclusters == assonumber:
        break

print ("Number of confirmed Associates: {}".format(len(confirmedAssociates)))
print (confirmedAssociates)


cmd = "mkdir {}/analysis/{}".format(db_dir, args.output)
os.system(cmd)

cmd = "mkdir {}/analysis/{}/consensussequences".format(db_dir, args.output)
os.system(cmd)

cmd = "mkdir {}/analysis/{}/newoutput/".format(db_dir, args.output)
os.system(cmd)

for i in range(len(confirmedAssociates)):
    cmd = "cp {}datafiles/isolatefiles/{}/* {}analysis/{}/consensussequences/.".format(db_dir, confirmedAssociates[i].split(" ")[0], db_dir, args.output)
    os.system(cmd)

cmd = "cp {}datafiles/isolatefiles/{}/* {}analysis/{}/consensussequences/.".format(db_dir, args.reference, db_dir, args.output)
os.system(cmd)

cmd = "rm {}analysis/{}/consensussequences/{}*".format(db_dir, args.output, args.reference)
os.system(cmd)


for i in range(len(confirmedAssociates)): #Don't include reference from other clusters
    cmd = "rm {}analysis/{}/consensussequences/{}".format(db_dir, args.output, confirmedAssociates[i].split(" ")[0])
    os.system(cmd)




infile = open("{}REFDB.ATG.name".format(db_dir), 'r')
linenumber = 1
for line in infile:
    line = line.rstrip()
    if line.split(" ")[0] == args.reference or line.split(" ")[0] == args.reference[0:-2]:
        header_text = line
        templateid = linenumber
    linenumber += 1
infile.close()

files = os.listdir("{}/analysis/{}/consensussequences/".format(db_dir, args.output))
files.sort()
complete_path_files = []


for i in range(len(files)):
    infile = open("{}analysis/{}/consensussequences/".format(db_dir, args.output) + files[i], 'r')
    sequence = ""
    for line in infile:
        line = line.rstrip()
        if line[0] == ">":
            header = line
        else:
            sequence += line
    infile.close()

    sequence = sequence.replace("a", "n")
    sequence = sequence.replace("t", "n")
    sequence = sequence.replace("c", "n")
    sequence = sequence.replace("g", "n")

    outfile = open("{}analysis/{}/consensussequences/".format(db_dir, args.output) + "hardmasked_" + files[i], 'w')
    print (header, file = outfile)
    print (sequence, file = outfile)
    outfile.close()
    complete_path_files.append("{}analysis/{}/consensussequences/".format(db_dir, args.output) + "hardmasked_" + files[i])


for i in range(len(complete_path_files)):
    cmd = "{} -i {} -o  {}/analysis/{}/newoutput/nc_{} -t_db {}/{} -ref_fsa -nf -na -ca -dense -cge -vcf -bc90 -Mt1 {}".format(kma_path, complete_path_files[i], db_dir, args.output, files[i], db_dir, "REFDB.ATG", templateid)
    os.system(cmd)

cmd = "{} dist -i {}/analysis/{}/newoutput/*.fsa -o {}/analysis/{}/distmatrix.phy -r \"{}\" -f 9 -mc 1 -nm 0".format(ccphylo_path, db_dir, args.output, db_dir, args.output, header_text)
os.system(cmd)


cmd = "{} tree -i {}/analysis/{}/distmatrix.phy -o {}/analysis/{}/tree.newick".format(ccphylo_path, db_dir, args.output, db_dir, args.output)
os.system(cmd)
moss.generateFigtree("{}/analysis/{}/tree.newick".format(db_dir, args.output), args.reference)

end_time = datetime.datetime.now()
run_time = end_time - start_time
print("Run time: {}".format(run_time))



import os
import sys
import gzip

def calc_allele_freq(vcf_line_list):
    freqs = []
    dp = int(vcf_line[7].split(";")[0].split("=")[-1])
    observations = vcf_line[7].split(";")[-1][4:].split(",")
    for item in observations:
        freqs.append(int(item)/dp)
    return freqs

def check_variant(vcf_line_list):
    ad6_list = ["A", "C", "G", "T", "N", "-"]
    freqs = calc_allele_freq(vcf_line_list)
    for i in range(len(freqs)):
        if freqs[i] > 0.6:
            msg = "{} has a {} at position {} which is a {} with a frequency of {}.".format(vcf_line_list[0], "major variant", vcf_line_list[1], ad6_list[i], freqs[i])
            print (msg)
        if freqs[i] > 0.2 and freqs[i] < 0.6:
            msg = "{} has a {} at position {} which is a {} with a frequency of {}.".format(vcf_line_list[0],
                                                                                            "minor variant",
                                                                                            vcf_line_list[1], ad6_list[i],
                                                                                            freqs[i])
            print(msg)

input_file = "../test273.vcf.gz"

variant_list = []

infile = gzip.open(input_file, 'rb')
for line in infile:
    line = line.decode()
    if line[0] != "#":
        vcf_line = line.rstrip().split("\t") #Load line, strip new line, decode to string, split to list
        #vcf_line is a list of [#chrom, pos, ID, REF, ALT, Qual, Filter, Info, Format]. We want to extract the info, so position 7 to check the depth
        depth = int(vcf_line[7].split(";")[0].split("=")[-1])
        if depth > 300:
            check_variant(vcf_line)
infile.close()
