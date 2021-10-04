# Copyright (c) 2019, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries
import sys
import os
import argparse
import operator
import time
import geocoder
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
from geopy.geocoders import Nominatim
from subprocess import check_output, STDOUT

#Utility functions




def sql_string_metadata(metadict):
    entries = ""
    values = ""
    for item in metadict:
        entries += item + ","
        values += "'{}',".format(metadict[item])
    entries = entries[:-1]
    values = values[:-1]
    return entries.replace("'", "''"), values




def prod_metadata_dict(metadata, metadata_headers):
    metadict = dict()
    if '\ufeff' in metadata:
        metadata = metadata.replace(u'\ufeff','').split(",")
    else:
        metadata = metadata.split(",")
    if '\ufeff' in metadata_headers:
        metadata_headers = metadata_headers.replace(u'\ufeff', '').split(",")
    else:
        metadata_headers = metadata_headers.split(",")
    for i in range(len(metadata_headers)):
        metadict[metadata_headers[i]] = metadata[i]
    return metadict

def check_to_destroy_shm_db(kma_path, kma_database_path, db_dir, logfile):
    with open(db_dir + "analyticalFiles/queuedAnalyses.json") as json_file:
        queue_json = json.load(json_file)
    json_file.close()

    with open(db_dir + "analyticalFiles/runningAnalyses.json") as json_file:
        running_json = json.load(json_file)
    json_file.close()

    if running_json == {} and queue_json == {}: #Take Down DB from shm
        os.system("{}_shm -t_db {} -destroy".format(kma_path, kma_database_path))
        print ("{}_shm -t_db {} -destroy".format(kma_path, kma_database_path), file=logfile)


def check_shm_kma(kma_path, kma_database_path, cmd, logfile):
    try: #Check if KMA db in shm
        cmd_stdout = check_output(cmd, stderr=STDOUT, shell=True).decode()
    except Exception as e:
        os.system("{}_shm -t_db {}".format(kma_path, kma_database_path)) #Loads DB
        os.system(cmd)
        return True

def correctPathCheck(pathName):
    if pathName == "":
        pass
    elif pathName[-1] == "/":
        pass
    else:
        pathName = pathName + "/"
    return pathName

def calc_coordinates_from_location(city, country):
    try:
        geolocator = Nominatim(user_agent="moss")
        loc = geolocator.geocode("{},{}".format(city, country))
        latitude = loc.latitude
        longitude = loc.longitude
    except:
        latitude = ""
        longitude = ""
    return latitude, longitude


def check_coordinates(coordinates):
    try:
        coordinates = geocoder.ip('me').latlng
        geolocator = Nominatim(user_agent="moss")
        location = geolocator.reverse(coordinates)
    except:
        coordinates = ""
        location = ""
    return coordinates, location


def check_alignment_kma_cov(file):
    infile = open(file, 'r')
    top_score = 0
    coverage = 0
    for line in infile:
        if line[0] != "#":
            line = line.rstrip()
            line = line.split("\t")
            if float(line[1]) > top_score:
                top_score = float(line[1])
                coverage = float(line[5])
    infile.close()

    return coverage

def findTemplateSurveillance(total_filenames, target_dir, kma_database_path, logfile, kma_path, mac):
    #Variable initilization
    template_found = False
    best_template = ""
    best_template_score = 0.0
    templatename = ""
    print("# Finding best template for Surveillance pipeline", file=logfile)
    if mac:
        cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 0 -nf -mem_mode -sasm -ef -mrs 0.".format(kma_path,
                                                                                                  total_filenames,
                                                                                                  target_dir,
                                                                                                  kma_database_path)
        os.system(cmd)
    else:
        cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 0 -nf -mem_mode -sasm -ef -shm -mrs 0".format(kma_path, total_filenames, target_dir, kma_database_path)
        print ("started here")
        check_shm_kma(kma_path, kma_database_path, cmd, logfile)
    print (cmd, file = logfile)
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


        template_found = True
        return best_template_score, template_found, templatename

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

def illuminaMappingForward(input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion,db_dir, mac):
    illumina_name = input[0].split("/")[-1]

    #Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running
    result, action = acquire_semaphore("IndexRefDB", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("IndexRefDB", db_dir)
    elif result != 'acquired' and action == True:
        result += " : IndexRefDB, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if mac:
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {}".format(
                kma_path, input[0][0], target_dir, illumina_name, templateaccesion, kma_database_path,
                str(best_template), str(multi_threading))
            os.system(cmd)
        else:

            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -nf -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0][0], target_dir, illumina_name, templateaccesion, kma_database_path,
                str(best_template), str(multi_threading))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Illumina mapping completed succesfully", file=logfile)
    #semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
    #assembly_semaphore_value = semaphore.value
    #if assembly_semaphore_value == 0:
    #    print("Another subprocess is currently writing to the reference database")
    #    try:
    #        semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
    #        semaphore.release()  # No database writing, clear to go#
    #
    #    except posix_ipc.BusyError as error:
    #        semaphore.unlink()
    #        sys.exit(
    #            "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")

   # semaphore = posix_ipc.Semaphore("/ReadRefDB", posix_ipc.O_CREAT, initial_value=100)
    #assembly_semaphore_value = semaphore.value
    #if assembly_semaphore_value == 0:
    #    print("100 processes are reading from reference DB -- waiting for free spot")
    #    try:
    #        semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
    #        if input[0] != "":
    #            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
    #                kma_path, input[0][0], target_dir, illumina_name, templateaccesion, kma_database_path,
    #                str(best_template), str(multi_threading))
    #            print(cmd, file=logfile)
    #            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
    #        print("# Illumina mapping completed succesfully", file=logfile)
    #        semaphore.release()
    #    except posix_ipc.BusyError as error:
    #        semaphore.unlink()
    #        sys.exit(
    #            "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")


def illuminaMappingPE(input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion, db_dir, mac):
    print (input, file=logfile)
    illumina_name = input[0].split("/")[-1]

    # Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running

    result, action = acquire_semaphore("IndexRefDB", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("IndexRefDB", db_dir)
    elif result != 'acquired' and action == True:
        result += " : IndexRefDB, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if mac:
            cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0], input[1], target_dir, illumina_name, templateaccesion,
                kma_database_path, str(best_template), str(multi_threading))
            os.system(cmd)
        else:
            cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0], input[1], target_dir, illumina_name, templateaccesion,
                kma_database_path, str(best_template), str(multi_threading))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Illumina mapping completed succesfully", file=logfile)

    """
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
            if input[0] != "":
                cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
                    kma_path, input[0], input[1], target_dir, illumina_name, templateaccesion,
                    kma_database_path, str(best_template), str(multi_threading))
                print (cmd, file=logfile)
                check_shm_kma(kma_path, kma_database_path, cmd, logfile)
            print("# Illumina mapping completed succesfully", file=logfile)

            semaphore.release()
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")
    else:
        semaphore.acquire(timeout=18000)
        if input[0] != "":
            cmd = "{} -ipe {} {} -o {}{}_{}_consensus -t_db {} -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(kma_path, input[0], input[0], target_dir, illumina_name, templateaccesion, kma_database_path, str(best_template), str(multi_threading))
            print(cmd, file=logfile)
            os.system(cmd)
        print ("# Illumina mapping completed succesfully", file=logfile)

        semaphore.release()
    """


def nanoporeMapping(input, best_template, target_dir, kma_database_path, logfile, multi_threading, bc, kma_path, templateaccesion, db_dir, mac):
    nanopore_name = input[0].split("/")[-1]

    # Claim ReafRefDB is IndexRefDB is free
    # Check if an assembly is currently running

    result, action = acquire_semaphore("IndexRefDB", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("IndexRefDB", db_dir)
    elif result != 'acquired' and action == True:
        result += " : IndexRefDB, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if mac:
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -nf -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {} -mct 0.1 -ml 400 -proxi -0.9 -mrc 0.7 -mrs 0.25".format(
                kma_path, input[0], target_dir, nanopore_name, templateaccesion, kma_database_path,
                str(best_template), str(multi_threading), str(bc))
            os.system(cmd)
        else:
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -nf -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {} -shm -mct 0.1 -ml 400 -proxi -0.9 -mrc 0.7 -mrs 0.25".format(
                kma_path, input[0], target_dir, nanopore_name, templateaccesion, kma_database_path,
                str(best_template), str(multi_threading), str(bc))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Nanopore mapping completed succesfully", file=logfile)

    """
    
    
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
            if input[0] != "":
                cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {} -shm".format(
                    kma_path, input[0], target_dir, nanopore_name, templateaccesion, kma_database_path,
                    str(best_template), str(multi_threading), str(bc))
                print(cmd, file=logfile)
                check_shm_kma(kma_path, kma_database_path, cmd, logfile)
            print("# Nanopore mapping completed succesfully", file=logfile)

            semaphore.release()
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit(
                "IndexRefDB semaphore is jammed, and so ReadRefDB could not be claim")
    else:
        semaphore.acquire(timeout=18000)
        if input[0] != "":
            cmd = "{} -i {} -o {}{}_{}_consensus -t_db {} -mp 20 -1t1 -dense -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {} -shm".format(kma_path, input[0], target_dir, nanopore_name, templateaccesion, kma_database_path, str(best_template), str(multi_threading), str(bc))
            print(cmd, file=logfile)
            os.system(cmd)
        print ("# Nanopore mapping completed succesfully", file=logfile)

        semaphore.release()
        
    """


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

def mossCheckInputFiles(input, seqType):
    if seqType == "nanopore":
        inputType = "nanopore"
        total_filenames = input[0]
        assemblyType = "nanopore"
    elif seqType == "pe_illumina":
        if len(input) != 2:
            sys.exit("You did not give 2 files, yet seqType was set to be pe_illumina")
        else:
            inputType = "pe_illumina"
            total_filenames = " ".join(input)
            assemblyType = "illumina"
    elif seqType == "se_illumina":
        if len(input) != 1:
            sys.exit("You gave more than 1 file, yet seqType was set to be se_illumina")
        else:
            inputType = "se_illumina"
            total_filenames = input[0]
            assemblyType = "illumina"
    else:
        sys.exit("Incorrent input or seqType")
    return inputType, total_filenames, assemblyType

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def claim_semaphore(semaphore, db_dir, value):
    isolatedb = db_dir + "moss.db"

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    dbstring = "UPDATE ipctable SET {} = '{}' WHERE ipc = '{}'".format(semaphore, int(value)-1, 'IPC')
    c.execute(dbstring)
    conn.commit()
    conn.close()

def acquire_semaphore(semaphore, db_dir, expected, time_limit):

    running_time = 0
    result = ""
    action = False
    semaphore_status = False
    value = check_sql_semaphore_value(db_dir, semaphore)

    if value != expected:
        while value != expected:
            print (running_time)
            time.sleep(10)
            running_time += 10
            value = check_sql_semaphore_value(db_dir, semaphore)
            if running_time >= time_limit:
                result = "Running time exceeded the 7200, a semaphore is likely jammed"
                action = True
                break
        claim_semaphore(semaphore, db_dir, value)
        result = "acquired"
    else:
        claim_semaphore(semaphore, db_dir, value)
        result = "acquired"

    return result, action

def release_semaphore(semaphore, db_dir):
    value = check_sql_semaphore_value(db_dir, semaphore)

    isolatedb = db_dir + "moss.db"

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    dbstring = "UPDATE ipctable SET {} = '{}'".format(semaphore, int(value) + 1)
    c.execute(dbstring)
    conn.commit()
    conn.close()




def check_sql_semaphore_value(db_dir, semaphore):
    isolatedb = db_dir + "moss.db"

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT {} FROM ipctable".format(semaphore))
    refdata = c.fetchall()
    conn.close()

    return int(refdata[0][0])


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

def scan_reference_vs_isolate_cge(plasmid_string, allresgenes, virulence_string, templatename, db_dir):

    plasmids_isolate = plasmid_string.split(",")
    amrgenes_isolate = allresgenes.split(",")
    virulencegenes_isolate = virulence_string.split(",")

    #This function checks if an isolate has any unique amrgenes, virulencegenes or plasmids vs the cluster and returns them if any are found
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM isolatetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()

    print (refdata)

    if refdata != []:
        if refdata[0][0] == None:
            plasmids_reference = []
        else:
            plasmids_reference = refdata[0][0].split(",")
    else:
        plasmids_reference= []

    c.execute("SELECT virulencegenes FROM isolatetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()
    if refdata != []:
        if refdata[0][0] == None:
            virulencegenes_reference = []
        else:
            virulencegenes_reference = refdata[0][0].split(",")
    else:
        virulencegenes_reference = []

    c.execute("SELECT amrgenes FROM isolatetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()
    if refdata != []:
        if refdata[0][0] == None:
            amrgenes_reference = []
        else:
            amrgenes_reference = refdata[0][0].split(",")
    else:
        amrgenes_reference = []


    conn.close()

    unique_plasmids = list(set(plasmids_isolate).symmetric_difference(set(plasmids_reference)))
    unique_virulence_genes = list(set(virulencegenes_isolate).symmetric_difference(set(virulencegenes_reference)))
    unique_amr_genes = list(set(amrgenes_isolate).symmetric_difference(set(amrgenes_reference)))

    if len(unique_plasmids) > 0:
        new_plasmid_string = plasmid_string + "," + ",".join(unique_plasmids)
    else:
        new_plasmid_string = None

    if len(unique_virulence_genes) > 0:
        new_virulence_string = virulence_string + "," + ",".join(unique_virulence_genes)
    else:
        new_virulence_string = None

    if len(unique_amr_genes) > 0:
        new_amr_string = allresgenes + "," + ",".join(unique_amr_genes)
    else:
        new_amr_string = None


    return new_plasmid_string, new_virulence_string, new_amr_string





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

    return ("{}tree.png".format(inputdir))

def inputAssemblyFunction(assemblyType, inputType, target_dir, input, illumina_name1, illumina_name2, jobid, inputname, kma_path, kma_database_path, entryid, referenceSyncFile, isolatedb, db_dir, associated_species):
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

            cmd = "cp {} {}dockertmp/{}".format(input[0], target_dir, illumina_name1)
            os.system(cmd)
            cmd = "cp {} {}dockertmp/{}".format(input[1], target_dir, illumina_name2)
            os.system(cmd)

            cmd = "docker run --name assembly_results{} -v {}dockertmp/:/dockertmp/ nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -1 /dockertmp/{} -2 /dockertmp/{} -o /dockertmp/assembly_results -t 4".format(
                jobid, target_dir, illumina_name1, illumina_name2)
            print(cmd)
            os.system(cmd)
        elif inputType == "se_illumina":
            cmd = "docker run --name assembly_results{} -v {}:/dockertmp/{} nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -s /dockertmp/{} -o /dockertmp/assembly_results -t 4".format(
                jobid, input[0], inputname, inputname)
            os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_results", jobid), shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/dockertmp/assembly_results {}.".format(id, target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)

        # Insert new reference in KMA reference db
        print("no template TRUE")
        # Unicycler illumina

        # concatenate all reads into one file

        infile = open("{}assembly_results/assembly.fasta".format(target_dir), 'r')
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

        #Here, prior to indexeing recheck with kma mapping for new reference hit, else add #DEVELOP

        result, action = acquire_semaphore("IndexRefDB", db_dir, 1, 7200)
        if result == 'acquired' and action == False:
            cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir,
                                                                     inputname)  # add assembly to references
            os.system(cmd)
            referencejson[inputname] = {'entryid': entryid, 'headerid': inputname,
                                        'filename': "{}_assembled.fasta".format(inputname)}
            with open(referenceSyncFile, 'w') as f_out:
                json.dump(referencejson, f_out)
            f_out.close()

            release_semaphore("IndexRefDB", db_dir)

        elif result != 'acquired' and action == True:
            result += " : IndexRefDB"
            sys.exit(result)
        else:
            sys.exit('A semaphore related issue has occured.')

        #semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        #assembly_semaphore_value = semaphore.value
        #if assembly_semaphore_value == 1:
        #   semaphore.acquire(timeout=3600)
        #else:
        #   print ("Another subprocess is currently writing to the reference database.")
        #   print ("Another subprocess is currently writing to the reference database.", file=logfile)
        #   try:
        #       semaphore.acquire(timeout=18000) #Wait maxium of 5 hours.
        #   except posix_ipc.BusyError as error:
        #       semaphore.unlink()
        #       print("IndexRefDB is jammed.")
        #       print("Unlinking semaphore")
        #       semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        #       semaphore.acquire(timeout=3600)
        #cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir, inputname)  # add assembly to references
        #os.system(cmd)
        #referencejson[inputname] = {'entryid': entryid, 'headerid': inputname, 'filename': "{}_assembled.fasta".format(inputname)}
        #with open(referenceSyncFile, 'w') as f_out:
        #    json.dump(referencejson, f_out)
        #f_out.close()
        #semaphore.release()

        conn = sqlite3.connect(isolatedb)
        c = conn.cursor()
        #Here, check and insert amrgenes, virulencegenes, plasmids.
        dbstring = "INSERT INTO referencetable(entryid, headerid, refname) VALUES ('{}', '{}', '{}')".format(entryid, associated_species, inputname)
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

        cmd = "docker run --name assembly_results{} -v {}:/tmp/{} nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -l /tmp/{} -o /tmp/assembly_results -t 4".format(
            jobid, input[0], inputname, inputname)
        os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_results", jobid), shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/tmp/assembly_results {}.".format(id, target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)

        # Concatenate contigs
        infile = open("{}assembly_results/assembly.fasta".format(target_dir), 'r')
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

        result, action = acquire_semaphore("IndexRefDB", db_dir, 1, 7200)
        if result == 'acquired' and action == False:
            cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir,
                                                                     inputname)  # add assembly to references
            os.system(cmd)
            referencejson[inputname] = {'entryid': entryid, 'headerid': inputname,
                                        'filename': "{}_assembled.fasta".format(inputname)}
            with open(referenceSyncFile, 'w') as f_out:
                json.dump(referencejson, f_out)
            f_out.close()

            release_semaphore("IndexRefDB", db_dir)

        elif result != 'acquired' and action == True:
            result += " : IndexRefDB"
            sys.exit(result)
        else:
            sys.exit('A semaphore related issue has occured.')

        #semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        #assembly_semaphore_value = semaphore.value
        #if assembly_semaphore_value == 1:
        #    semaphore.acquire(timeout=3600)
        #else:
        #    print("Another subprocess is currently writing to the reference database.")
        #    print("Another subprocess is currently writing to the reference database.", file=logfile)
        #    try:
        #        semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
        #    except posix_ipc.BusyError as error:
        #        semaphore.unlink()
        #        print("IndexRefDB is jammed.")
        #        print("Unlinking semaphore")
        #        semaphore = posix_ipc.Semaphore("/IndexRefDB", posix_ipc.O_CREAT, initial_value=1)
        #        semaphore.acquire(timeout=3600)

        #cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir, inputname)  # add assembly to references
        #os.system(cmd)
        #referencejson[inputname] = {'entryid': entryid, 'headerid': inputname, 'filename': "{}_assembled.fasta".format(inputname)}
        #with open(referenceSyncFile, 'w') as f_out:
        #    json.dump(referencejson, f_out)
        #f_out.close()
        #semaphore.release()

        conn = sqlite3.connect(isolatedb)
        c = conn.cursor()
        dbstring = "INSERT INTO referencetable(entryid, headerid, refname) VALUES('{}', '{}', '{}')".format(entryid, associated_species, inputname)
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


def uniqueNameCheck(db_dir, inputType, total_filenames):
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

    conn = sqlite3.connect(db_dir + "moss.db")
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

    #Mangler, check for value, if 0, ergo assembly quit


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

def findTemplateNumber(db_dir, name):
    infile = open(db_dir + "REFDB.ATG.name", 'r')
    t = 1
    for line in infile:
        if line.rstrip() == name:
            return t
        else:
            t = t + 1


def initRunningAnalyses(db_dir, outputname, inputname, entryid):

    with open(db_dir + "analyticalFiles/runningAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    time = str(datetime.datetime.now())[0:-7]

    class runningAnalysis:
        def __init__(self, entryid, starttime, filename):
            self.entryid = entryid
            self.start_time = starttime
            self.file_name = filename

    analysis = runningAnalysis(entryid,time,inputname)

    jsonStr = json.dumps(analysis.__dict__)

    referencejson[entryid] = jsonStr

    with open("{}analyticalFiles/runningAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(referencejson, f_out)
    f_out.close()

def endRunningAnalyses(db_dir, outputname, inputname, entryid):
    with open(db_dir + "analyticalFiles/runningAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    referencejson.pop(entryid, None)

    with open("{}analyticalFiles/runningAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(referencejson, f_out)
    f_out.close()


    with open(db_dir + "analyticalFiles/finishedAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    time = str(datetime.datetime.now())[0:-7]

    class finishedAnalysis:
        def __init__(self, entryid, finishtime, filename):
            self.entryid = entryid
            self.finish_time = finishtime
            self.file_name = filename

    analysis = finishedAnalysis(entryid, time, inputname)

    jsonStr = json.dumps(analysis.__dict__)

    referencejson[entryid] = jsonStr

    with open("{}analyticalFiles/finishedAnalyses.json".format(db_dir), 'w') as f_out:
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

def run_quast(target_dir, jobid):
    cmd = "docker run --name quast{} -v {}/assembly_results/:/data/assembly_results/ staphb/quast quast.py /data/assembly_results/assembly.fasta -o /output/quast_output".format(
        jobid, target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("quast", jobid), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/output/quast_output {}quast_output".format(id, target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)



def matrixClusterSize(db_dir, templatename):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT isolateid FROM referencetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()
    conn.close()
    length = len(refdata[0][0].split(", "))
    return length

def lastClusterAddition(db_dir, templatename):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT entryid, analysistimestamp FROM isolatetable WHERE headerid = '{}' ORDER BY analysistimestamp DESC".format(templatename)) #Dårlig løsning, ikke skalerbar til >5M isolates
    refdata = c.fetchall()
    conn.close()
    return refdata

def isolate_file_name(db_dir, entryid):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT isolatename FROM isolatetable WHERE entryid = '{}'".format(entryid))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0][0]

    return element


def generate_amr_resistance_profile_table(db_dir, entryid, pdf, target_dir, exepath, templatename):

    panel_found = False
    panel_list = []

    genus = templatename.split()[1]
    species = templatename.split()[2]

    panels = []
    antimicrobials = dict()

    infile = open(exepath + "resfinder/db_resfinder/phenotype_panels.txt" ,'r')
    add_amr_flag = False
    for line in infile:
        line = line.rstrip()
        if line != "" and line[0] != "#":
            line = line.split()
            if line[0] == ":Panel:":
                if len(line) == 3:
                    panels.append("{} {}".format(line[1], line[2]))
                    antimicrobials["{} {}".format(line[1], line[2])] = []
                    add_amr_flag = True
                else:
                    panels.append(line[1])
                    antimicrobials[line[1]] = []
                    add_amr_flag = True
            elif add_amr_flag == True:
                if line[0] == ":Include:":
                    for item in antimicrobials[line[1]]:
                        antimicrobials[panels[-1]].append(item)
                else:
                    antimicrobials[panels[-1]].append(line[0])
        else:
            add_amr_flag = False
    infile.close()

    if "{} {}".format(genus, species) in panels:
        panel_found = True
        panel_list = antimicrobials["{} {}".format(genus, species)]
    elif genus in panels:
        if len(antimicrobials[genus]) > 1:
            panel_found = True
            panel_list = antimicrobials[genus]


    # antiomicrobial, Class, Resistant/no resitance, match, genes.
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT phenotypes FROM amrtable WHERE entryid = '{}'".format(entryid))
    refdata = c.fetchall()
    conn.close()

    outfile = open(target_dir + "amr.csv", 'w')
    header = "Antimicrobial,Class,Resistance,Match,Genes"
    reflist = refdata[0][0].split(";")

    print (header, file=outfile)

    if panel_found:
        for item in reflist:
            item = item.split(",")
            if (item[0][0].upper() + item[0][1:]) in panel_list:
                if item[4] != "":
                    item[4] = "\"" + item[4].replace("@", ", ") + "\""
                item = ",".join(item)
                print(item, file=outfile)
    else:
        #Are we missing potential genes?
        for item in reflist:
            item = item.split(",")
            if item[0].split()[0] != "unknown":
                if item[4] != "":
                    item[4] = "\"" + item[4].replace("@", ", ") + "\""
                item = ",".join(item)
                print (item, file=outfile)
    outfile.close()

    return reflist, panel_found, panel_list

def time_of_analysis(db_dir, entryid):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT analysistimestamp FROM isolatetable WHERE entryid = '{}'".format(entryid))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0][0]



    return element

def run_bandage(target_dir, jobid):
    cmd = "docker run --name bandage{} -v {}/assembly_results/:/data/assembly_results/ nanozoo/bandage Bandage image /data/assembly_results/assembly.gfa contigs.jpg".format(
        jobid, target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("bandage", jobid), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:contigs.jpg {}contigs.jpg".format(id, target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)


def compileReportAssembly(target_dir, ID, db_dir, image_location, associated_species, exepath):
    #QA checks?
    #Quast?

    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(ID)  # ADD idd

    ''' First Page '''
    pdf.add_page()
    pdf.image(exepath + "/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, ID, "MOSS analytical report")
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "Sample name: {} \n" \
                 "No reference cluster was identified. \n" \
                 "".format(ID, associated_species) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    run_quast(target_dir, ID)

    cmd = "/opt/homebrew/bin/Rscript {}src/quast_tsv_table.R {}".format(exepath, target_dir)
    os.system(cmd)
    run_bandage(target_dir, ID)
    pdf.image("{}quast_table.png".format(target_dir), x=118, y=60, w=pdf.w / 2.7, h=pdf.h / 2.1)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.cell(85, 5, "Contig visualization:", 0, 1, 'L')
    pdf.image("{}contigs.jpg".format(target_dir), x=15, y=70, w=pdf.w / 2.2, h=pdf.h / 2.7)



    pdf.output(target_dir + filename, 'F')


def retrieve_cge_counts(target_dir, ID, db_dir, image_location, templatename, exepath):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM isolatetable WHERE entryid = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        plasmids_isolate = []
    else:
        plasmids_isolate = refdata[0][0].split(",")

    c.execute("SELECT virulencegenes FROM isolatetable WHERE entryid = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        virulencegenes_isolate = []
    else:
        virulencegenes_isolate = refdata[0][0].split(",")

    c.execute("SELECT amrgenes FROM isolatetable WHERE entryid = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        amrgenes_isolate = []
    else:
        amrgenes_isolate = refdata[0][0].split(",")

    c.execute("SELECT plasmids FROM referencetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        plasmids_reference = []
    else:
        plasmids_reference = refdata[0][0].split(",")

    c.execute("SELECT virulencegenes FROM referencetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        virulencegenes_reference = []
    else:
        virulencegenes_reference = refdata[0][0].split(",")

    c.execute("SELECT amrgenes FROM referencetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        amrgenes_reference = []
    else:
        amrgenes_reference = refdata[0][0].split(",")

    conn.close()



    return plasmids_isolate, virulencegenes_isolate, amrgenes_isolate, plasmids_reference, virulencegenes_reference, amrgenes_reference






def compileReportAlignment(target_dir, ID, db_dir, image_location, templatename, exepath, logfile):
    print ("no init=", file=logfile)
    pdf = FPDF()  # A4 (210 by 297 mm)
    print ("step 0", file = logfile)

    filename = "{}_report.pdf".format(ID) #ADD idd
    clusterSize = int(matrixClusterSize(db_dir, templatename)) + 2
    latestAddition = lastClusterAddition(db_dir, templatename)
    phenotypes, panel_found, panel_list = generate_amr_resistance_profile_table(db_dir, ID, pdf, target_dir, exepath, templatename)
    print ("step 1", file = logfile)

    ''' First Page '''
    pdf.add_page()
    pdf.image(exepath + "/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, ID, "MOSS analytical report")
    pdf.ln(5)
    file_name = isolate_file_name(db_dir, ID)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "Sample name: {} \n" \
                 "Identifilessed reference: {} \n" \
                 "".format(ID, file_name, templatename)
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(10)

    analysistimestamp = time_of_analysis(db_dir, ID)
    pdf.set_font('Arial', '', 10)
    #Cell here
    print ("step 2", file = logfile)

    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 153, 255)
    pdf.set_xy(x=10, y=60)
    pdf.cell(85, 5, "Sample information: ", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = "Copenhagen, Denmark \n" \
                 "Time of sampling: 2019-06-11 18:03:00. \n" \
                 "Number of associated isolates: {} \n" \
                 "Latest addition to cluster: {}. \n" \
                 "".format(clusterSize, latestAddition[0][1])
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)
    pdf.set_text_color(51, 153, 255)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "CGE results: ", 0, 1, 'L')
    print ("step 3", file = logfile)

    plasmids_isolate, virulencegenes_isolate, amrgenes_isolate, plasmids_reference, virulencegenes_reference, amrgenes_reference = retrieve_cge_counts(target_dir, ID, db_dir, image_location, templatename, exepath)
    textstring = "AMR genes in this sample: {}. \n" \
                 "AMR genes in this cluster: {}. \n" \
                 "Plasmids in this sample: {}. \n" \
                 "Plasmids in this cluster: {}. \n" \
                 "Virulence genes in this sample: {}. \n" \
                 "Virulence genes in this cluster: {}. \n" \
                 "".format(len(amrgenes_isolate), len(amrgenes_reference), len(plasmids_isolate), len(plasmids_reference), len(virulencegenes_reference), len(virulencegenes_reference))
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)
    print("pre-r", file=logfile)

    #Rsub-script is not called when page is left
    if panel_found:
        cmd = "/opt/homebrew/bin/Rscript {}src/moss_csv_to_frontside_table.R {}".format(exepath, target_dir)
        print (cmd, file =logfile)
        os.system(cmd)
        print ("did it work?", file=logfile)
        time.sleep(35)
        #here the r script does not produce an image #Sub process stops
        pdf.image("{}amr_table.png".format(target_dir), x=90, y=60, w=pdf.w / 1.95, h=pdf.h / 1.75)

    else:
        pdf.cell(85, 5, "Organism was not in annotated panel. The following AMR genes were found:", 0, 1, 'L')
        cmd = "/opt/homebrew/bin/Rscript {}src/moss_csv_to_frontside_table.R {}".format(exepath, target_dir)
        os.system(cmd)
        #subprocess.run(cmd)
        print ("did it work?", file=logfile)
        time.sleep(5)

        pdf.image("{}amr_table.png".format(target_dir), x=90, y=60, w=pdf.w / 1.95, h=pdf.h / 1.75)

    pdf.ln(10)

    pdf.set_font('Arial', '', 12)

    ''' Second Page '''
    pdf.add_page()
    pdf.image(exepath + "/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, ID, "Phylogeny results")
    pdf.ln(20)
    pdf.image(image_location, x=10, y=35, w=pdf.w/1.6, h=pdf.h/1.6)


    pdf.output(target_dir + filename, 'F')
"""

    ''' finder pages'''
    #pdf.add_page()
    #pdf.ln(20)
    #resfinderPage(target_dir + "resfinderResults/ResFinder_results_tab.txt", pdf, target_dir)
    pdf.add_page()
    pdf.ln(20)
    virulencePage(target_dir + "virulenceFinderResults/data.json", pdf, target_dir)
    pdf.add_page()
    pdf.ln(20)
    plasmidPage(target_dir + "plasmidFinderResults/data.json", pdf, target_dir)
    plasmid_count, plasmid_list = plasmid_data_for_report(target_dir + "plasmidFinderResults/data.json", pdf, target_dir)
    pdf.output(target_dir + filename, 'F')

    compare_plasmid_isolate_vs_cluster(plasmid_list, templatename, db_dir)"""

def compare_plasmid_isolate_vs_cluster(plasmid_list, templatename, db_dir):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM referencetable WHERE headerid = '{}'".format(templatename))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0]


    if refdata[0][0] == None:
        list = []
    else:
        list = refdata[0][0].split(",")
    return list


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


def plasmid_data_for_report(jsoninput, target_dir):
    if os.path.isfile(jsoninput):
        with open(jsoninput) as json_file:
            data = json.load(json_file)
        count1 = 0
        plasmid_list = []
        for species in data['plasmidfinder']['results']:
            for hit in data['plasmidfinder']['results'][species]:
                if type(data['plasmidfinder']['results'][species][hit]) == dict:
                    print (data['plasmidfinder']['results'][species][hit])
                    for gene in data['plasmidfinder']['results'][species][hit]:
                        count1 += 1
                        plasmid_list.append(gene)
    else:
        count1 = 0
        plasmid_list = []
    return count1, plasmid_list

def virulence_data_for_report(jsoninput, target_dir, logfile):
    print("#t1 ", file=logfile)
    #HERE SOMETHINIG HAPPEND CHECK
    if os.path.isfile(jsoninput):
        with open(jsoninput) as json_file:
            data = json.load(json_file)
        count1 = 0
        print("#t2 ", file=logfile)

        virulence_list = []
        for species in data['virulencefinder']['results']:
            print("#t3 ", file=logfile)

            for hit in data['virulencefinder']['results'][species]:
                if type(data['virulencefinder']['results'][species][hit]) == dict:
                    print (data['virulencefinder']['results'][species][hit])
                    print("#t4 ", file=logfile)

                    for gene in data['virulencefinder']['results'][species][hit]:
                        count1 += 1
                        virulence_list.append(gene)
                        print("#t5 ", file=logfile)
    else:
        count1 = 0
        virulence_list = []

    return count1, virulence_list



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

def create_title(pdf, id, string):
  # Unicode is not yet supported in the py3k version; use windows-1252 standard font
  pdf.set_text_color(51, 153, 255)
  pdf.set_font('Arial', 'BU', 36)
  pdf.ln(10)
  pdf.write(5, f"{string}")
  pdf.ln(10)
  pdf.set_text_color(0, 0, 0)

def queueMultiAnalyses(db_dir, inputlist):
    with open(db_dir + "analyticalFiles/queuedAnalyses.json") as json_file:
        _json = json.load(json_file)
    json_file.close()
    class Analysis:
        def __init__(self, entryid, filename):
            self.entryid = entryid
            self.file_name = filename
    for i in range(len(inputlist)):
        entryid = md5(inputlist[i])
        _analysis = Analysis(entryid, inputlist[i].split("/")[-1])
        jsonStr = json.dumps(_analysis.__dict__)
        entryid = md5(inputlist[i])
        _json[entryid] = jsonStr

    with open("{}analyticalFiles/queuedAnalyses.json".format(db_dir), 'w') as f_out:
        json.dump(_json, f_out)
    f_out.close()

def processQueuedAnalyses(db_dir, outputname, inputname, entryid):
    with open(db_dir + "analyticalFiles/queuedAnalyses.json") as json_file:
        referencejson = json.load(json_file)
    json_file.close()

    if entryid in referencejson:
        referencejson.pop(entryid, None)
        with open("{}analyticalFiles/queuedAnalyses.json".format(db_dir), 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()

        with open(db_dir + "analyticalFiles/runningAnalyses.json") as json_file:
            referencejson = json.load(json_file)
        json_file.close()

        time = str(datetime.datetime.now())[0:-7]

        class runningAnalysis:
            def __init__(self, entryid, starttime, filename):
                self.entryid = entryid
                self.start_time = starttime
                self.file_name = filename

        analysis = runningAnalysis(entryid, time, inputname)

        jsonStr = json.dumps(analysis.__dict__)

        referencejson[entryid] = jsonStr

        with open("{}analyticalFiles/runningAnalyses.json".format(db_dir), 'w') as f_out:
            json.dump(referencejson, f_out)
        f_out.close()
    else:
        initRunningAnalyses(db_dir, outputname, inputname, entryid)

def checkAMRrisks(target_dir, entryid, db_dir, templatename, exepath, logfile):
    warning = []
    riskcategory = []
    tabfile = target_dir + "resfinderResults/ResFinder_results_tab.txt"
    infile = open(tabfile, 'r')
    allresgenes = []
    resdata = []
    for line in infile:
        line = line.rstrip().split("\t")
        if line[0] != "Resistance gene": #Skip first line
            resdata.append(line[7].upper())
            if line[0] not in allresgenes:
                allresgenes.append(line[0])
    infile.close()

    pheno_file = target_dir + "resfinderResults/pheno_table.txt"
    infile = open(pheno_file, 'r')
    amrinfo = []
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split("\t")
            if len(line) > 1:
                if len(line) == 5:
                    nlist = line[4].split(", ")
                    tlist = []
                    for item in nlist:
                        id = item.split(" ")[0]
                        tlist.append(id)
                    line[4] = "@".join(tlist)
                else:
                    line.append("")
                line = ",".join(line)
                amrinfo.append(line)

    infile.close()


    with open(exepath + "datafiles/AMR_Watch_list.json") as json_file:
        amr_list = json.load(json_file)
    json_file.close()


    templatenamelist = templatename.split()
    speciename = (templatenamelist[1] + " " + templatenamelist[2]).upper()

    for category in amr_list:
        for specie in amr_list[category]:
            if specie.upper() in speciename: #If the species from the isolate is in the watch list
                if type(amr_list[category][specie]) == list:
                    for risk_gene in amr_list[category][specie]:
                        for resistance_gene in resdata:
                            if risk_gene.upper() in resistance_gene:  # If match is found as substring in any resistance hit from ResFinder
                                msg = "{}: {}".format(speciename, resistance_gene)
                                risk = category
                                if msg not in warning:
                                    warning.append(msg)
                                if risk not in riskcategory:
                                    riskcategory.append(risk)
                else:
                    for resistance_gene in resdata:
                        if amr_list[category][specie].upper() in resistance_gene: #If match is found as substring in any resistance hit from ResFinder
                            msg = "{}: {}".format(speciename, resistance_gene)
                            risk = category
                            if msg not in warning:
                                warning.append(msg)
                            if risk not in riskcategory:
                                riskcategory.append(risk)
    if warning == []:
        warning = ""
    else:
        warning = ", ".join(warning)
    if len(riskcategory) > 1:
        riskcategory = str(max(riskcategory))
    elif len(riskcategory) == 1:
        riskcategory = str(riskcategory[0])
    else:
        riskcategory = "0"
    if allresgenes == []:
        allresgenes = ""
    else:
        allresgenes = ", ".join(allresgenes)
    if amrinfo == []:
        amrinfo = ""
    else:
        amrinfo = ";".join(amrinfo)
    return warning, riskcategory, allresgenes, amrinfo










