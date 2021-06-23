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
import threading
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3
import json
import datetime
import hashlib
import gzip
import posix_ipc
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import gzip
from fpdf import FPDF
from pandas.plotting import table
#Utility functions
def correctPathCheck(pathName):
    if pathName == "":
        pass
    elif pathName[-1] == "/":
        pass
    else:
        pathName = pathName + "/"
    return pathName

def findTemplateSurveillance(total_filenames, target_dir, kma_database_path, logfile, kma_path):
    #Variable initilization
    template_found = False
    best_template = ""
    best_template_score = 0.0
    templatename = ""
    print("# Finding best template for Surveillance pipeline", file=logfile)
    #cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 50 -Sparse -mp 20".format(kma_path, total_filenames, target_dir, kma_database_path)
    #os.system(cmd)
    cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 0 -mem_mode -sasm -ef".format(kma_path, total_filenames, target_dir, kma_database_path)
    os.system(cmd)

    ###
    #Currently, facing the issue of only have 1 output in reference list. why? ask Philip
    try:
        best_template_score = 0
        templatename = ""
        infile = open("{}template_kma_results.res".format(target_dir), 'r')
        for line in infile:
            line = line.rstrip()
            line = line.split("\t")
            if line[0][0] != "#":
                if float(line[1]) > best_template_score:
                    best_template_score = float(line[1])
                    templatename = line[0]


        #cmd = "sort -n -k 2 -r -t$\'\\t\' {}template_kma_results.res > {}sorted_template_kma_results.res".format(target_dir, target_dir)
        #print (cmd, file = logfile)
        #os.system(cmd)
        #infile_template = open(target_dir + "sorted_template_kma_results.res", 'r')
        #templateline = infile_template.readlines()[1]
        #infile_template.close()

        #templatedict = {}
        ##template_ids = []
        #templatename = templateline.split("\t")[0]
        #best_template_score = float(line.split("\t")[1])
        #template_ids.append(templateid)
        #templatedict[templatename] = templateid
        #print("best score:" + str(best_template_score), file=logfile)
        template_found = True
        return best_template_score, template_found, templatename

        #print("Best template: " + str(templatename))


        #sasmsparsematch = false#
        #
        #infile = open(target_dir + "template_kma_results.spa", 'r')
        #for line in infile:
        #    line = line.rstrip()
        #    line = line.split("\t")
        #    if line[0] == templatename :
       #        sasmsparsematch = true


        #print("Best templatenum: " + str(best_template))
        #print("Best template: " + str(templatename))
        #print("best score:" + str(best_template_score))
        #print("Best templatenumber: " + str(best_template), file=logfile)
        #print("Best template: " + str(templatename), file=logfile)
        #print("best score:" + str(best_template_score), file=logfile)
        #cmd = "rm {}temp_search*".format(target_dir)


        #Optimize getting linenumber using subprocess
        #cmd = "wc -l {}template_kma_results.spa > {}linenumber".format(target_dir, target_dir)
        #os.system(cmd)
        #infile = open(target_dir + "linenumber", 'r')
        #line = infile.readlines()[0]
        #linecount = int(line.split(" ")[0])
        #template_ids = []
        #if linecount >= 10:
        #    readinglines = 11
        #else:
        #    readinglines = linecount
        #t = 0
        #infile_template.close()
        #infile_template = open(target_dir + "template_kma_results.spa", 'r')
        ##Look at top-10 (at max) templates
        #templatedict = {}

        #for templateline in infile_template:
        #    if t != 0:
        #        templatename = templateline.split("\t")[0]
        #        templateid = templateline.split("\t")[1]
        #        template_ids.append(templateid)
        #        templatedict[templatename] = templateid
        #    elif t == readinglines:
        #        break
        #    else:
        #        t = t + 1
        #print ("template ids are: " + str(template_ids))
        #print ("template ids are: " + str(template_ids), file=logfile)


        #print (templatedict)

        #Create minidatabase of top 10 templates, to confirmed the final template
        #for i in range(len(template_ids)):
        #    cmd = "{} seq2fasta -t_db {} -seqs {} > {}temp_template_{}".format(kma_path, kma_database_path, template_ids[i], target_dir, template_ids[i])
        #    os.system(cmd)
        #cmd = "{} index -i {}temp_template* -o {}temp_search_db".format(kma_path, target_dir, target_dir)
        #os.system(cmd)

        #cmd = "{} -i {} -o {}template_kma_results_nonsparse -ID 50 -t_db {}temp_search_db -mp 20".format(kma_path, total_filenames, target_dir, target_dir)
        #os.system(cmd)
        #cmd = "rm {}linenumber".format(target_dir)
        #os.system(cmd)
        #infile_template.close()
        #infile_template = open(target_dir + "template_kma_results_nonsparse.res", 'r')
        #line = infile_template.readlines()[1]
        #best_template = line.split("\t")[1]
        #templatename = line.split("\t")[0]
        # scoring of matches, loop through and fine all maatches of 97%> BTD
        #qq

        #Retrieve original template number of best template:
        #best_template = templatedict[templatename]

        #print ("Best templatenum: " + str(best_template))
        #print ("Best template: " + str(templatename))
        #print ("best score:" + str(best_template_score))
        #print("Best templatenumber: " + str(best_template), file=logfile)
        #print("Best template: " + str(templatename), file=logfile)
        #print("best score:" + str(best_template_score), file=logfile)
        #cmd = "rm {}temp_search*".format(target_dir)
        #os.system(cmd)
        #infile_template.close()
        #works
        #if best_template_score >= 90.00:
        #    template_found = True
        #    infile_template.close()
        #    return best_template, best_template_score, template_found, templatename
        #else:
        #    print("The input could not score > 95.00 template score. Thus input will be assembled and be made a new reference.")
        #    template_found = False
        #    return best_template, best_template_score, template_found, templatename

    #If no match are found, the sample will be defined as a new reference.
    except IndexError as error:
        print(
            "None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.")
        print(
            "None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.",
            file=logfile)
        # Perform assembly based on input
        template_found = False
        print("FoundnoTemplate")
        return best_template_score, template_found, templatename
    ###

def illuminaMappingForward(illumina_input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion):
    illumina_name = illumina_input[0][-1]

    #Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running
    semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("Another subprocess is currently writing to the reference database")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            semaphore.release()  # No database writing, clear to go

        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")

    semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("100 processes are reading from reference DB -- waiting for free spot")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            if illumina_input != "":
                cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {}".format(
                    kma_path, illumina_input[0], target_dir, illumina_name, templateaccesion, kma_database_path,
                    str(best_template), str(multi_threading))
                os.system(cmd)
            print("# Illumina mapping completed succesfully", file=logfile)
            semaphore.release()
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")
    else:
        semaphore.acquire(timeout=18000)
        if illumina_input != "":
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {}".format(kma_path, illumina_input[0], target_dir, illumina_name, templateaccesion, kma_database_path, str(best_template), str(multi_threading))
            os.system(cmd)
        print ("# Illumina mapping completed succesfully", file=logfile)

        semaphore.release()


def illuminaMappingPE(illumina_input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion):
    illumina_name = illumina_input[0].split("/")[-1]

    # Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running
    semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("Another subprocess is currently writing to the reference database")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            semaphore.release()  # No database writing, clear to go
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")

    semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("100 processes are reading from reference DB -- waiting for free spot")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            if illumina_input != "":
                cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {}".format(
                    kma_path, illumina_input[0], illumina_input[1], target_dir, illumina_name, templateaccesion,
                    kma_database_path, str(best_template), str(multi_threading))
                os.system(cmd)
            print("# Illumina mapping completed succesfully", file=logfile)

            semaphore.release()
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")
    else:
        semaphore.acquire(timeout=18000)
        if illumina_input != "":
            cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {}".format(kma_path, illumina_input[0], illumina_input[1], target_dir, illumina_name, templateaccesion, kma_database_path, str(best_template), str(multi_threading))
            os.system(cmd)
        print ("# Illumina mapping completed succesfully", file=logfile)

        semaphore.release()


def nanoporeMapping(nanopore_input, best_template, target_dir, kma_database_path, logfile, multi_threading, bc, kma_path, templateaccesion):
    nanopore_name = nanopore_input.split("/")[-1]

    # Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running
    semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("Another subprocess is currently writing to the reference database")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            semaphore.release()  # No database writing, clear to go
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")

    semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print("100 processes are reading from reference DB -- waiting for free spot")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            if nanopore_input != "":
                cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {}".format(
                    kma_path, nanopore_input, target_dir, nanopore_name, templateaccesion, kma_database_path,
                    str(best_template), str(multi_threading), str(bc))
                print(cmd)
                os.system(cmd)
            print("# Nanopore mapping completed succesfully", file=logfile)

            semaphore.release()
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")
    else:
        semaphore.acquire(timeout=18000)
        if nanopore_input != "":
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {}".format(kma_path, nanopore_input, target_dir, nanopore_name, templateaccesion, kma_database_path, str(best_template), str(multi_threading), str(bc))
            print (cmd)
            os.system(cmd)
        print ("# Nanopore mapping completed succesfully", file=logfile)

        semaphore.release()


def loadFiles(path):
    if path != "":
        files = os.listdir(path)
        files.sort()
    else:
        files = ""
    return files

def generate_complete_path_illumina_files(illumina_files, illumina_path_input):
    path = illumina_path_input
    complete_path_illumina_files = []
    for i in range(len(illumina_files)):
        complete_path_illumina_files.append(path + illumina_files[i])
    return complete_path_illumina_files

def generate_complete_path_nanopore_files(nanopore_files, nanopore_path_input):
    path = nanopore_path_input
    complete_path_nanopore_files = []
    for i in range(len(nanopore_files)):
        complete_path_nanopore_files.append(path + nanopore_files[i])
    return complete_path_nanopore_files

def combine_input_files(illumina_files, nanopore_files):
    if illumina_files == "":
        total_input_files = nanopore_files
    elif nanopore_files == "":
        total_input_files = illumina_files
    else:
        total_input_files = illumina_files + nanopore_files
    total_input_files = " ".join(total_input_files)
    return total_input_files

def logfileConditionsResearch(logfile, masking_scheme, prune_distance, bc, ref_kma_database, multi_threading, reference, output_name):
    logdict = {}
    if masking_scheme != "":
        logdict['masking_scheme'] = masking_scheme
    else:
        logdict['masking_scheme'] = ""
    if prune_distance != 10:
        logdict['prune_distance'] = prune_distance
    else:
        logdict['prune_distance'] = 10
    if bc != 0.7:
        logdict['bc'] = bc
    else:
        logdict['bc'] = 0.7
    if ref_kma_database != "":
        logdict['ref_kma_database'] = ref_kma_database
    else:
        logdict['ref_kma_database'] = ""
    if multi_threading != 1:
        logdict['multi_threading'] = multi_threading
    else:
        logdict['multi_threading'] = 1
    if reference != "":
        logdict['reference'] = reference
    else:
        logdict['reference'] = ""
    if output_name != "":
        logdict['output_name'] = output_name
    else:
        logdict['output_name'] = ""
    print (logdict, file=logfile)

def varriansfileRenamer(total_filenames):
    inputs = total_filenames.split(" ")
    sorted_input = []
    for i in range(len(inputs)):
        name = inputs[i].split("/")[-1]
        sorted_input.append(name)

def concatenateDraftGenome(input_file):
    cmd = "grep -c \">\" {}".format(input_file)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = int(output.decode().rstrip())
    input_name = input_file.split("/")[-1]
    new_name = ""
    if id > 1:
        input_path = "/".join(input_file.split("/")[:-1])
        new_name = input_path + "concatenated_" + input_name
        infile = open(input_file, 'r')
        writefile = open(new_name, 'w')
        sequence = ""
        for line in infile:
            if line[0] != ">":
                line = line.rstrip()
                sequence += line
        print(">concatenated_" + input_name, file=writefile)
        print(sequence, file=writefile)
        infile.close()
        writefile.close()
    return id, new_name

def mossCheckInputFiles(i_illumina, i_nanopore):
    if i_illumina != "" and i_nanopore != "":
        sys.exit("Please only give one file at a time for the surveillance pipeline.")
    elif len(i_nanopore) > 0:
        inputType = "nanopore"
        total_filenames = i_nanopore
        assemblyType = "nanopore"
    elif len(i_illumina) == 2:
        inputType = "pe_illumina"
        total_filenames = " ".join(i_illumina)
        assemblyType = "illumina"
    elif len(i_illumina) == 1:
        inputType = "se_illumina"
        total_filenames = i_illumina[0]
        assemblyType = "illumina"
    else:
        sys.exit("You did not give input files in the correct format. Make sure you either submit one nanopore readfile, OR either one forward illumina file or two paired end illumina files.")
    return inputType, total_filenames, assemblyType

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def inputHeader(total_files, inputType):
    if inputType == "nanopore" or inputType == "se_illumina":
        if total_files[-3:] == ".gz":
            infile = open(total_files, 'rb')
        else:
            infile = open(total_files, 'r')
        first_line = infile.readline().rstrip()
    elif inputType == "pe_illumina":
        infile = open(total_files[0], 'r')
        first_line = infile.readline().rstrip()
    return first_line[1::]

def databaseOverClustering(db_dir, dbname, kma_path, filename):
    cmd = "{} dist -t_db {}{} -d 1 -o {}referenceCluster -tmp {}".format(kma_path, db_dir, dbname, db_dir, db_dir)
    os.system(cmd)
    distancematrix = []
    infile = open("{}referenceCluster".format(db_dir), 'r')
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

def ThreshholdDistanceCheck(distancematrixfile, reference, isolate):
    infile = open(distancematrixfile, 'r')
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == reference or line[0] == isolate:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == reference or line[0] == isolate:
                index = linecount
                secondentry = True
        linecount += 1

def generateFigtree(inputfile, jobid):
    cmd = "docker run --name figtree{} -v {}:/tmp/tree.tree biocontainers/figtree:v1.4.4-3-deb_cv1 figtree -graphic PNG -width 500 -height 500 /tmp/tree.tree /tmp/tree.png".format(jobid, inputfile)
    os.system(cmd)

    filelist = inputfile.split("/")
    namelenght = len(filelist[-1])
    inputdir = inputfile[0:-namelenght]


    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("figtree", jobid), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/tree.png {}tree.png".format(id, inputdir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    return (inputdir + "tree.png")

def inputAssemblyFunction(assemblyType, inputType, target_dir, i_illumina, illumina_name1, illumina_name2, i_nanopore, jobid, inputname, kma_path, kma_database_path, entryid, referenceSyncFile, isolatedb, db_dir):
    with open(referenceSyncFile) as json_file:
        referencejson = json.load(json_file)
    json_file.close()
    if assemblyType == "illumina":
        # IF NO GOOD REFERENCE FOUND; QUIT WITH MESSAGE
        # Not yet working, fix soon

        # Make tmp dir for docker

        if inputType == "pe_illumina":
            cmd = "mkdir {}dockertmp".format(target_dir)
            os.system(cmd)

            cmd = "cp {} {}dockertmp/{}".format(i_illumina[0], target_dir, illumina_name1)
            os.system(cmd)
            cmd = "cp {} {}dockertmp/{}".format(i_illumina[1], target_dir, illumina_name2)
            os.system(cmd)

            cmd = "docker run --name illumina_assembly{} -v {}dockertmp/:/dockertmp/ nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -1 /dockertmp/{} -2 /dockertmp/{} -o /dockertmp/illumina_assembly -t 4".format(
                jobid, target_dir, illumina_name1, illumina_name2)
            print(cmd)
            os.system(cmd)
        elif inputType == "se_illumina":
            cmd = "docker run --name illumina_assembly{} -v {}:/dockertmp/{} nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -s /dockertmp/{} -o /dockertmp/illumina_assembly -t 4".format(
                jobid, i_illumina[0], inputname, inputname)
            os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("illumina_assembly", jobid), shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/dockertmp/illumina_assembly {}.".format(id, target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)

        # Insert new reference in KMA reference db
        print("no template TRUE")
        # Unicycler illumina

        # concatenate all reads into one file

        infile = open("{}illumina_assembly/assembly.fasta".format(target_dir), 'r')
        writefile = open("{}{}_assembled.fasta".format(target_dir, inputname), 'w')  # Adds all contigs to one sequence
        sequence = ""
        for line in infile:
            if line[0] != ">":
                line = line.rstrip()
                sequence += line
        print(">" + inputname, file=writefile)
        print(sequence, file=writefile)
        infile.close()
        writefile.close()

        #Assembly complete

        semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        assembly_semaphore_value = semaphore.value
        if assembly_semaphore_value == 1:
           semaphore.acquire(timeout=3600)
        else:
           print ("Another subprocess is currently writing to the reference database.")
           print ("Another subprocess is currently writing to the reference database.", file=logfile)
           try:
               semaphore.acquire(timeout=18000) #Wait maxium of 5 hours.
           except posix_ipc.BusyError as error:
               semaphore.unlink()
               print("IndexRefDB is jammed.")
               print("Unlinking semaphore")
               semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
               semaphore.acquire(timeout=3600)
        cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir, inputname)  # add assembly to references
        os.system(cmd)
        referencejson[inputname] = {'entryid': entryid, 'headerid': inputname, 'filename': "{}_assembled.fasta".format(inputname)}
        with open(referenceSyncFile, 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()
        semaphore.release()

        conn = sqlite3.connect(isolatedb)
        c = conn.cursor()
        dbstring = "INSERT INTO referencetable(entryid, headerid, refname) VALUES ('{}', '{}', '{}')".format(entryid, inputname, inputname)
        c.execute(dbstring)
        conn.commit()  # Need IPC
        conn.close()

        cmd = "mkdir {}datafiles/isolatefiles/{}".format(db_dir, inputname)
        os.system(cmd)

        cmd = "mkdir {}datafiles/distancematrices/{}".format(db_dir, inputname)
        os.system(cmd)

        # Works
        print("illumina")



    elif assemblyType == "nanopore":
        ##docker pull nanozoo/unicycler:0.4.7-0--c0404e6
        # Insert new reference in KMA reference db
        print("no template TRUE runnning nanopore assembly")
        # Longread assembly

        cmd = "docker run --name nanopore_assembly{} -v {}:/tmp/{} nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -l /tmp/{} -o /tmp/nanopore_assembly -t 4".format(
            jobid, i_nanopore, inputname, inputname)
        os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("nanopore_assembly", jobid), shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/tmp/nanopore_assembly {}.".format(id, target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)

        # Concatenate contigs
        infile = open("{}nanopore_assembly/assembly.fasta".format(target_dir), 'r')
        writefile = open("{}{}_assembled.fasta".format(target_dir, inputname), 'w')  # Adds all contigs to one sequence
        sequence = ""
        for line in infile:
            if line[0] != ">":
                line = line.rstrip()
                sequence += line
        print(">" + inputname, file=writefile)
        print(sequence, file=writefile)
        infile.close()
        writefile.close()

        # Assembly complete

        semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        assembly_semaphore_value = semaphore.value
        if assembly_semaphore_value == 1:
            semaphore.acquire(timeout=3600)
        else:
            print("Another subprocess is currently writing to the reference database.")
            print("Another subprocess is currently writing to the reference database.", file=logfile)
            try:
                semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            except posix_ipc.BusyError as error:
                semaphore.unlink()
                print("IndexRefDB is jammed.")
                print("Unlinking semaphore")
                semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
                semaphore.acquire(timeout=3600)

        cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir, inputname)  # add assembly to references
        os.system(cmd)
        referencejson[inputname] = {'entryid': entryid, 'headerid': inputname, 'filename': "{}_assembled.fasta".format(inputname)}
        with open(referenceSyncFile, 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()
        semaphore.release()

        conn = sqlite3.connect(isolatedb)
        c = conn.cursor()
        dbstring = "INSERT INTO referencetable(entryid, headerid, refname) VALUES('{}', '{}', '{}')".format(entryid, inputname, inputname)
        c.execute(dbstring)
        conn.commit()  # Need IPC
        conn.close()

        cmd = "mkdir {}datafiles/isolatefiles/{}".format(db_dir, inputname)
        os.system(cmd)

        cmd = "mkdir {}datafiles/distancematrices/{}".format(db_dir, inputname)
        os.system(cmd)

        cmd = "cp {}{}_assembled.fasta {}datafiles/distancematrices/{}/{}_assembled.fasta".format(target_dir, inputname, db_dir, inputname, inputname)
        os.system(cmd)

        # Works


def uniqueNameCheck(dbdir, inputType, total_filenames):
    if inputType == "nanopore":
        inputpath = total_filenames
        isolatename = inputpath.split("/")[-1]
    elif inputType == "pe_illumina":
        inputpath = total_filenames.split(" ")[0]
        isolatename = inputpath.split("/")[-1]
    elif inputType == "se_illumina":
        inputpath = total_filenames
        isolatename = inputpath.split("/")[-1]

    if inputType == "nanopore" or inputType == "se_illumina":
        if total_filenames[-3:] == ".gz":
            infile = gzip.open(total_filenames, 'rb')
            first_line = infile.readline().rstrip().decode("utf8")
        else:
            infile = open(total_filenames, 'r')
            first_line = infile.readline().rstrip()
    elif inputType == "pe_illumina":
        if total_filenames.split(" ")[0][-3:] == ".gz":
            infile = gzip.open(total_filenames.split(" ")[0], 'rb')
            first_line = infile.readline().rstrip().decode("utf8")
        else:
            infile = open(total_filenames.split(" ")[0], 'r')
            first_line = infile.readline().rstrip()

    header = first_line[1:]
    if first_line[0] == ">": #Reference
        print (header)
        if " " in header:
            accession = header.split(" ")[0]
        else:
            accession = header

    else:
        accession = inputpath.split("/")[-1]

    conn = sqlite3.connect(dbdir + "moss.db")
    c = conn.cursor()

    c.execute("SELECT * FROM isolatetable WHERE isolatename = '{}'".format(isolatename))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An isolate sample has the same filename as your input. Please change your input file's name.")

    c.execute("SELECT * FROM referencetable WHERE refname = '{}'".format(accession))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An reference sample has the same filename or header string as your input. Please change your input file's name.")

    c.execute("SELECT * FROM referencetable WHERE headerid = '{}'".format(header))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An reference sample has the same filename or header string as your input. Please change your input file's name.")


    conn.close()

def semaphoreInitCheck():
    # Check if an assembly is currently running
    semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1) 
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print ("Another subprocess is currently writing to the reference database")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            semaphore.release()  # No database writing, clear to go
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit("IndexRefDB semaphore is jammed. A process waited > 5H to write to the reference database. Run CleanSemaphore.py to wipe all phores")

    # Check if an assembly is currently running
    semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100) #Maximum of 100 readers
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        try:
            semaphore.acquire(timeout=3600)  # Wait max 1h to see if someone is writing to database
            semaphore.release()  # No database writing, clear to go
        except posix_ipc.BusyError as error:
            print("ReadRefDB semaphore is jammed. Unlinking it by running cleanSemaphore.py")
            semaphore.unlink()

    # Check if an assembly is currently running
    #semaphore = posix_ipc.Semaphore("/IsolateJSON", posix_ipc.O_CREAT, initial_value=1)
    #assembly_semaphore_value = semaphore.value
    #if assembly_semaphore_value == 0:
    #    try:
    #        semaphore.acquire(timeout=3600)  # Wait max 1h to see if someone is writing to database
    #    except posix_ipc.BusyError as error:
    #        print("IsolateJSON semaphore is jammed. Unlinking it now.")
    #        semaphore.unlink()
    #semaphore.release()  # No assembly running, clear to go

def findTemplateNumber(db_dir, name):
    infile = open(db_dir + "REFDB.ATG.name", 'r')
    t = 1
    for line in infile:
        if line.rstrip() == name:
            return t
        else:
            t = t + 1


def initRunningAnalyses(dbdir, outputname, inputname, entryid):

    with open(dbdir + "analyticalFiles/runningAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    time = str(datetime.datetime.now())[0:-7]

    class runningAnalysis:
        def __init__(self, name, starttime, filename):
            self.name = name
            self.start_time = starttime
            self.file_name = filename

    analysis = runningAnalysis(outputname,time,inputname)

    jsonStr = json.dumps(analysis.__dict__)

    referencejson[entryid] = jsonStr

    with open("{}analyticalFiles/runningAnalyses.json".format(dbdir), 'w') as f_out:
        json.dump(referencejson, f_out)
    f_out.close()

def endRunningAnalyses(dbdir, outputname, inputname, entryid):
    with open(dbdir + "analyticalFiles/runningAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    referencejson.pop(entryid, None)

    with open("{}analyticalFiles/runningAnalyses.json".format(dbdir), 'w') as f_out:
        json.dump(referencejson, f_out)
    f_out.close()


    with open(dbdir + "analyticalFiles/finishedAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    time = str(datetime.datetime.now())[0:-7]

    class finishedAnalysis:
        def __init__(self, name, finishtime, filename):
            self.name = name
            self.finish_time = finishtime
            self.file_name = filename

    analysis = finishedAnalysis(outputname, time, inputname)

    jsonStr = json.dumps(analysis.__dict__)

    referencejson[entryid] = jsonStr

    with open("{}analyticalFiles/finishedAnalyses.json".format(dbdir), 'w') as f_out:
        json.dump(referencejson, f_out)
    f_out.close()

def makeDBinfo(isolatedb):
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    c.execute("SELECT * FROM isolatetable")
    refdata = c.fetchall()
    isolatenumber = len(refdata)
    c.execute("SELECT * FROM referencetable")
    refdata = c.fetchall()
    referencenumber = len(refdata)
    conn.close()

def runResFinder(exepath, total_filenames, target_dir):
    cmd = "python3 {}resfinder/run_resfinder.py -ifq {} -o {}resfinderResults -b {}resfinder/cge/ncbi-blast-2.10.1+/bin/blastn -acq".format(exepath, total_filenames, target_dir, exepath)
    os.system(cmd)

def runPlasmidFinder(exepath, total_filenames, target_dir):
    cmd = "mkdir {}plasmidFinderResults".format(target_dir)
    os.system(cmd)
    cmd = "python3 {}plasmidfinder/plasmidfinder.py -i {} -o {}plasmidFinderResults -mp {}kma/kma -p {}plasmidfinder/plasmidfinder_db".format(exepath, total_filenames, target_dir, exepath, exepath)
    os.system(cmd)

def runVirulenceFinder(exepath, total_filenames, target_dir):
    cmd = "mkdir {}virulenceFinderResults".format(target_dir)
    os.system(cmd)
    cmd = "python3 {}virulencefinder/virulencefinder.py -i {} -o {}virulenceFinderResults -mp {}kma/kma -p {}virulencefinder/virulencefinder_db".format(exepath, total_filenames, target_dir, exepath, exepath)
    os.system(cmd)


def compileReportAssembly(day, target_dir, ID, db_dir, image_location):
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(ID) #ADD idd

    ''' First Page '''
    pdf.add_page()
    create_title(day, pdf, ID)
    pdf.ln(10)
    pdf.set_font('Arial', 'BU', 12)
    pdf.write(5, "ASSEMBLY HERE")
    pdf.output(target_dir + filename, 'F')


def compileReportIsolate(day, target_dir, ID, db_dir, image_location):
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(ID) #ADD idd

    ''' First Page '''
    pdf.add_page()
    create_title(day, pdf, ID)
    pdf.ln(10)
    pdf.set_font('Arial', 'BU', 12)
    pdf.write(5, "Highest scoring reference: SomeReference")
    pdf.ln(10)
    pdf.write(5, "REFRENCESCORE")
    pdf.ln(10)
    pdf.write(5, "Associated Cluster: INSERT TREE HERE")
    #pdf.image(image_location)  # Works?
    pdf.ln(10)
    pdf.write(5, "Cluster information: INSERT HERE")
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.write(5, "Related patients' notes, genes, symptoms")
    pdf.ln(10)
    pdf.write(5, "Number of resistance genes: X, number of unique phenotypic resistances: Y symptoms")
    pdf.ln(10)
    pdf.write(5, "Virulence overview")
    pdf.ln(10)
    pdf.write(5, "Plasmid overview")
    pdf.ln(10)


    ''' Second Page '''

    ''' finder pages'''
    pdf.add_page()
    pdf.ln(20)
    resfinderPage(target_dir + "resfinderResults/ResFinder_results_tab.txt", pdf, target_dir)
    pdf.add_page()
    pdf.ln(20)
    virulencePage(target_dir + "virulenceFinderResults/data.json", pdf, target_dir)
    pdf.add_page()
    pdf.ln(20)
    plasmidPage(target_dir + "plasmidFinderResults/data.json", pdf, target_dir)
    pdf.output(target_dir + filename, 'F')

def resfinderPage(tabfile, pdf, target_dir):
    infile = open(tabfile, 'r')
    t = 0
    data = []
    for line in infile:
        line = line.rstrip().split("\t")
        if t == 0:
            line[2] = "Gene Length"
        else:
            if line[7] == "Warning: gene is missing from Notes file. Please inform curator.":
                line[7] = "NA."
        data.append(line)
        t += 1
    infile.close()
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "ResFinder Profile:")
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 7)
    table = tabulate(data, headers='firstrow', tablefmt='plain')
    pdf.write(5, f"{table}")

def virulencePage(jsoninput, pdf, target_dir):
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "VirulenceFinder Profile:")
    pdf.ln(10)
    with open(jsoninput) as json_file:
        data = json.load(json_file)
    for species in data['virulencefinder']['results']:
        pdf.set_font('Arial', 'B', 14)
        pdf.write(5, f"{species}")
        pdf.ln(5)
        for hit in data['virulencefinder']['results'][species]:
            pdf.set_font('Arial', 'B', 8)
            if type(data['virulencefinder']['results'][species][hit]) == dict:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.ln(5)
                for gene in data['virulencefinder']['results'][species][hit]:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.write(5, f"{gene}")
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 8)
                    for info in data['virulencefinder']['results'][species][hit][gene]:
                        string = "       {} : {}".format(info, data['virulencefinder']['results'][species][hit][gene][info])
                        pdf.write(5, f"{string}")
                        pdf.ln(5)
                    pdf.ln(10)
            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 8)
                pdf.write(5, f"{data['virulencefinder']['results'][species][hit]}")
                pdf.ln(10)

def plasmidPage(jsoninput, pdf, target_dir):
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "PlasmidFinder Profile:")
    pdf.ln(10)
    with open(jsoninput) as json_file:
        data = json.load(json_file)
    for species in data['plasmidfinder']['results']:
        pdf.set_font('Arial', 'B', 14)
        pdf.write(5, f"{species}")
        pdf.ln(5)
        for hit in data['plasmidfinder']['results'][species]:
            pdf.set_font('Arial', 'B', 8)
            if type(data['plasmidfinder']['results'][species][hit]) == dict:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.ln(5)
                for gene in data['plasmidfinder']['results'][species][hit]:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.write(5, f"{gene}")
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 8)
                    for info in data['plasmidfinder']['results'][species][hit][gene]:
                        string = "       {} : {}".format(info, data['plasmidfinder']['results'][species][hit][gene][info])
                        pdf.write(5, f"{string}")
                        pdf.ln(5)
                    pdf.ln(10)
            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 8)
                pdf.write(5, f"{data['plasmidfinder']['results'][species][hit]}")
                pdf.ln(10)

def create_title(day, pdf, id):
  # Unicode is not yet supported in the py3k version; use windows-1252 standard font
  pdf.set_font('Arial', '', 32)
  pdf.ln(25)
  pdf.write(5, f"MOSS Analytics Report")
  pdf.ln(10)
  pdf.set_font('Arial', '', 16)
  pdf.write(4, f'{day} {id}')
  pdf.ln(5)


def queueMultiAnalyses(dbdir, outputname, inputlist):
    with open(dbdir + "analyticalFiles/queuedAnalyses.json") as json_file:
        _json = json.load(json_file)
    json_file.close()
    class Analysis:
        def __init__(self, name, filename):
            self.name = outputname
            self.file_name = filename
    for i in range(len(inputlist)):
        _analysis = Analysis(outputname + str(i), inputlist[i].split("/")[-1])
        jsonStr = json.dumps(_analysis.__dict__)
        entryid = md5(inputlist[i])
        _json[entryid] = jsonStr

    with open("{}analyticalFiles/queuedAnalyses.json".format(dbdir), 'w') as f_out:
        json.dump(_json, f_out)
    f_out.close()

def processQueuedAnalyses(dbdir, outputname, inputname, entryid):
    with open(dbdir + "analyticalFiles/queuedAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    if entryid in referencejson:
        referencejson.pop(entryid, None)
        with open("{}analyticalFiles/queuedAnalyses.json".format(dbdir), 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()

        with open(dbdir + "analyticalFiles/runningAnalyses.json") as json_file:
            referencejson = json.load(json_file)
        json_file.close()

        time = str(datetime.datetime.now())[0:-7]

        class runningAnalysis:
            def __init__(self, name, starttime, filename):
                self.name = name
                self.start_time = starttime
                self.file_name = filename

        analysis = runningAnalysis(outputname, time, inputname)

        jsonStr = json.dumps(analysis.__dict__)

        referencejson[entryid] = jsonStr

        with open("{}analyticalFiles/runningAnalyses.json".format(dbdir), 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()
    else:
        initRunningAnalyses(dbdir, outputname, inputname, entryid)
