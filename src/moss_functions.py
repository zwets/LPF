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

import pandas as pd
from tabulate import tabulate
from IPython.display import display, HTML
import gzip
from fpdf import FPDF
from pandas.plotting import table
from geopy.geocoders import Nominatim
from subprocess import check_output, STDOUT
import mbh_helpers as mbh_helper
import moss_sql as moss_sql
from Bio import Phylo
import matplotlib.pyplot as plt
import pylab


#Utility functions

def get_kma_template_number(header_text, db_dir):
    infile = open(db_dir + "REFDB.ATG.name", 'r')
    t = 1
    number = 0
    for line in infile:
        if header_text in line:
            infile.close()
            return t
        t += 1
    infile.close()
    return t

def make_phytree_output_folder(db_dir, target_dir, isolate_list, exepath, header_text):
    cmd = "mkdir {}/phytree_output".format(target_dir)
    os.system(cmd)

    for item in isolate_list:
        path = "{}consensus_sequences/{}".format(db_dir, item)
        cmd = "cp {} {}/phytree_output/.".format(path, target_dir)
        os.system(cmd)

    number = get_kma_template_number(header_text, db_dir)
    header_name = header_text.split()[0]
    cmd = "{}/kma/kma seq2fasta -t_db {}REFDB.ATG -seqs {} > {}/phytree_output/{}.fsa".format(exepath, db_dir, number, target_dir, header_name)
    os.system(cmd)

    cmd = "cp {}*_consensus.fsa {}phytree_output/.".format(target_dir, target_dir)
    os.system(cmd)

def create_phylo_tree(db_dir, header_text, target_dir):
    tree = Phylo.read("{}phytree_output/tree.newick".format(target_dir), 'newick')
    Phylo.draw(tree, do_show=False)
    pylab.savefig("{}phytree_output/tree.png".format(target_dir))
    image_location = "{}/phytree_output/tree.png".format(target_dir)
    return image_location



def moss_shortcut_init(exepath):
    outfile = open(exepath + 'src/moss', 'w')
    print ("#!/usr/bin/env bash", file = outfile)
    print ("echo \'HELLO THERE\'", file = outfile)
    outfile.close()
    cmd = "mv {}src/moss ~/bin/.".format(exepath)
    os.system(cmd)
    cmd = "chmod a+x ~/bin/moss"
    os.system(cmd)

def init_insert_reference_table(exepath, db_dir):
    infile = open(db_dir + "REFDB.ATG.name", 'r')
    t = 1
    conn = sqlite3.connect(db_dir + 'moss.db')
    c = conn.cursor()
    ids = list()

    for line in infile:
        line = line.rstrip()
        cmd = "{}kma/kma seq2fasta -t_db {}/REFDB.ATG -seqs {}".format(exepath, db_dir, t)
        proc = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0].decode()
        header_text = output.split("\n")[0][1:]
        sequence = output.split("\n")[1]
        entryid = md5(sequence)
        #TMP SOLUTION TO AVOID ENTRYCLASHES:
        if entryid not in ids:
            dbstring = "INSERT INTO referencetable(entryid, header_text, amrgenes, virulencegenes, plasmids) VALUES('{}', '{}' ,'{}', '{}' ,'{}')".format(entryid, header_text.replace("'", "''"), "", "", "", "")
            ids.append(entryid)
            c.execute(dbstring)

        t += 1
    conn.commit()
    conn.close()

def check_assembly_result(path):

    return True

def run_assembly(entryid, db_dir, samplename, assemblyType, inputType, target_dir, input, illumina_name1, illumina_name2, \
                 jobid, exepath, kma_database_path, start_time, logfile, associated_species):
    moss_sql.update_status_table(entryid, "Unicycler Assembly", "Assembly", "4", "5", "Running", db_dir)
    if assemblyType == "illumina":
        inputAssemblyFunction(assemblyType, inputType, target_dir, input, illumina_name1, illumina_name2, "",
                                   jobid, samplename, exepath + "kma/kma", kma_database_path, entryid,
                                   db_dir + "moss.db", db_dir, associated_species)
    elif assemblyType == "nanopore":
        inputAssemblyFunction(assemblyType, inputType, target_dir, input, "", "", jobid, samplename,
                                   exepath + "kma/kma", kma_database_path, entryid, db_dir + "moss.db", db_dir,
                                   associated_species)
    time = datetime.datetime.now()-start_time
    mbh_helper.print_to_logfile("Run time: {}".format(time, True))
    moss_sql.update_status_table(entryid, "Compiling Assembly PDF", "Assembly", "5", "5", "Running", db_dir)

    compileReportAssembly(target_dir, entryid, db_dir, associated_species, exepath)

    logfile.close()
    moss_sql.update_status_table(entryid, "Assembly completed", "Assembly", "5", "5", "Finished", db_dir)
    sys.exit("No template was found, so input was added to references.")

def init_moss_variables(exepath, db_dir, ):
    referenceSyncFile = db_dir + "syncFiles/referenceSync.json"
    isolateSyncFile = db_dir + "syncFiles/isolateSync.json"
    return kma_path

def update_pip_dependencies():
    cmd = "python3 -m pip install --upgrade fpdf"
    os.system(cmd)
    cmd = "python3 -m pip install --upgrade tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    pip_list = ["geocoder", "pandas", "geopy", "Nominatim"]
    for item in pip_list:
        cmd = "pip install --upgrade {}".format(item)
        os.system(cmd)


def update_moss_dependencies(exepath, laptop, update_list, force):
    if force:
        if laptop:
            print ("laptop FORCE TBD")
        else:
            cmd = "cd {}".format(exepath)
            os.system(cmd)
            cmd = "rm -rf kma; rm -rf ccphylo; rm -rf mlst; rm -rf resfinder; rm -rf plasmidfinder; rm -rf virulencefinder;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder.git; cd resfinder; git checkout nanopore_flag; git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git db_resfinder; cd db_resfinder; git checkout minimizer_implementation; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git db_pointfinder; cd db_pointfinder; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/plasmidfinder.git; cd plasmidfinder; git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git; cd plasmidfinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/virulencefinder.git; cd virulencefinder; git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git; cd virulencefinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "apt-get install r-base"
            os.system(cmd)
            cmd = "apt install nodejs"
            os.system(cmd)
            cmd = "apt install npm"
            os.system(cmd)
            cmd = "apt install python3-pip"
            os.system(cmd)
            cmd = "apt install docker.io;  systemctl enable --now docker;  usermod -a -G docker $USER;"
            os.system(cmd)

    else:
        if laptop:
            print ("laptop SOFT TBD")
        else:
            if "kma" in update_list:
                cmd = "cd {}".format(exepath)
                os.system(cmd)
                cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
                os.system(cmd)
            if "ccphylo" in update_list:
                cmd = "cd {}".format(exepath)
                os.system(cmd)
                cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
                os.system(cmd)
            if "docker" in update_list:
                print ("Please make a manual installation of Docker and then run the python docker_images.py script")
            if "r" in update_list:
                cmd = " apt-get install r-base"
                os.system(cmd)
            if "npm" in update_list:
                cmd = " apt install npm"
                os.system(cmd)
            if "python3-pip" in update_list:
                cmd = " apt install python3-pip"
                os.system(cmd)
            if "conda" in update_list:
                print ("Please download conda manually for a full installation!")
    update_pip_dependencies()


def varify_tool(cmd, expected, index_start, index_end):
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode()
    version = output[index_start:index_end]
    print ("{} => {}".format(cmd, version))
    if version >= expected:
        return True
    else:
        return False

def varify_all_dependencies(exepath, laptop):
    update_list = []
    if not varify_tool("{}/kma/kma -v".format(exepath), '1.3.24', -8, -2):#KMA, expected: KMA-1.3.24+
        update_list.append("kma")
    if not varify_tool("{}/ccphylo/ccphylo -v".format(exepath), '0.5.3', -6, -1): #ccphylo, expected: CCPhylo-0.5.3
        update_list.append("ccphylo")
    if not varify_tool("docker -v".format(exepath), '20.10.8', 15, 22): #docker, Docker version 20.10.8, build 3967b7d28e
        update_list.append("docker")
    if not laptop:
        pass #Test CUDA
        #ont-guppy test
    if not varify_tool("R --version".format(exepath), '4.0.0', 10, 15): #R
        update_list.append("r")
    if not varify_tool("npm -v".format(exepath), '7.0.0', 0, -1): #npm 7.21.1
        update_list.append("npm")
    if not varify_tool("pip --version".format(exepath), '21.0.0', 4, 10): #pip, pip 21.3.1 from /user/etc/etc
        update_list.append("python3-pip")
    if not varify_tool("conda --version".format(exepath), '4.0.0', 6, -1): #conda, conda 4.10.1
        update_list.append("conda")
    return update_list




def run_mlst(exepath, total_filenames, target_dir, header_text, seqType):

    specie = header_text.split()[1].lower() + " " + header_text.split()[2].lower() #Make broader implementation here - fx "ecoli" is for e.coli mlst - how does that worK?

    mlst_dict = dict()
    infile = open(exepath + "mlst/mlst_db/config", 'r')
    for line in infile:
        if line[0] != "#":
            line = line.split("\t")
            mlst_dict[line[1].lower()] = line[0]
    infile.close()

    if specie == "escherichia coli":
        mlst_dict['escherichia coli'] = 'ecoli'


    if specie in mlst_dict:
        cmd = "mkdir {}/mlstresults".format(target_dir)
        os.system(cmd)
        if seqType == 'nanopore':
            cmd = "python3 {}mlst/mlst.py -i {} -o {}mlstresults -mp {}kma/kma -p {}/mlst/mlst_db/ -s {} -nano".format(exepath, total_filenames, target_dir, exepath, exepath, mlst_dict[specie])
            os.system(cmd)
        else:
            cmd = "python3 {}mlst/mlst.py -i {} -o {}mlstresults -mp {}kma/kma -p {}/mlst/mlst_db/ -s {}".format(exepath,
                                                                                                            total_filenames,
                                                                                                            target_dir,
                                                                                                            exepath,
                                                                                                            exepath,
                                                                                                            mlst_dict[specie])
            os.system(cmd)
        print (cmd)
        return True
    else:
        print ("no mlst")
        return False




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

#def check_to_destroy_shm_db(kma_path, kma_database_path, db_dir, logfile):
#    conn = sqlite3.connect(db_dir + "moss.db")
#    c = conn.cursor()
##    c.execute("SELECT * FROM ipctable WHERE header_text = '{}'".format(header_text))
#    refdata = c.fetchall()
#    conn.close()
#
#    if running_json == {} and queue_json == {}: #Take Down DB from shm
#        os.system("{}_shm -t_db {} -destroy".format(kma_path, kma_database_path))
#        print ("{}_shm -t_db {} -destroy".format(kma_path, kma_database_path), file=logfile)


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

def KMA_mapping(total_filenames, target_dir, kma_database_path, logfile, kma_path, laptop):
    template_found = False
    best_template = ""
    best_template_score = 0.0
    header_text = ""
    
    if laptop:
        cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 0 -nf -mem_mode -sasm -ef".format(kma_path,
                                                                                                  total_filenames,
                                                                                                  target_dir,
                                                                                                  kma_database_path)
        os.system(cmd)
    else:
        #tmp disabled shm
        cmd = "{} -i {} -o {}template_kma_results -t_db {} -ID 0 -nf -mem_mode -sasm -ef".format(kma_path, total_filenames, target_dir, kma_database_path)
        os.system(cmd)
        #check_shm_kma(kma_path, kma_database_path, cmd, logfile)
    try:
        infile = open("{}template_kma_results.res".format(target_dir), 'r')
        for line in infile:
            line = line.rstrip()
            line = line.split("\t")
            if line[0][0] != "#":
                if float(line[1]) > best_template_score:
                    best_template_score = float(line[1])
                    header_text = line[0]


        template_found = True
        return best_template_score, template_found, header_text

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
        return best_template_score, template_found, header_text
    ###

def illuminaMappingForward(input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion,db_dir, laptop, consensus_name):
    illumina_name = input[0].split("/")[-1]

    #Claim ReafRefDB is ipc_index_refdb is free
    # Check if an assembly is currently running
    result, action = acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("ipc_index_refdb", db_dir)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if laptop:
            cmd = "{} -i {} -o {} -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {}".format(
                kma_path, input[0][0], target_dir + consensus_name, kma_database_path,
                str(best_template), str(multi_threading))
            os.system(cmd)
        else:

            cmd = "{} -i {} -o {} -t_db {} -ref_fsa -ca -dense -cge -nf -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0][0], target_dir + consensus_name, kma_database_path,
                str(best_template), str(multi_threading))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Illumina mapping completed succesfully", file=logfile)


def illuminaMappingPE(input, best_template, target_dir, kma_database_path, logfile, multi_threading, kma_path, templateaccesion, db_dir, laptop, consensus_name):
    print (input, file=logfile)
    illumina_name = input[0].split("/")[-1]

    # Claim ReafRefDB is ipc_index_refdb is free
    # Check if an assembly is currently running

    result, action = acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("ipc_index_refdb", db_dir)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if laptop:
            cmd = "{} -ipe {} {} -o {} -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0], input[1], target_dir + consensus_name,
                kma_database_path, str(best_template), str(multi_threading))
            os.system(cmd)
        else:
            cmd = "{} -ipe {} {} -o {} -t_db {} -ref_fsa -ca -dense -nf -cge -vcf -bc90 -Mt1 {} -t {} -shm".format(
                kma_path, input[0], input[1], target_dir + consensus_name,
                kma_database_path, str(best_template), str(multi_threading))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Illumina mapping completed succesfully", file=logfile)


def nanoporeMapping(input, best_template, target_dir, kma_database_path, logfile, multi_threading, bc, kma_path, templateaccesion, db_dir, laptop, consensus_name):
    nanopore_name = input[0].split("/")[-1]

    # Claim ReafRefDB is ipc_index_refdb is free
    # Check if an assembly is currently running

    result, action = acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("ipc_index_refdb", db_dir)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')

    if input[0] != "":
        if laptop:
            cmd = "{} -i {} -o {} -t_db {} -mp 20 -1t1 -dense -nf -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {}".format(
                kma_path, input[0], target_dir + consensus_name, kma_database_path,
                str(best_template), str(multi_threading), str(bc))
            os.system(cmd)
        else:
            cmd = "{} -i {} -o {} -t_db {} -mp 20 -1t1 -dense -nf -vcf -ref_fsa -ca -bcNano -Mt1 {} -t {} -bc {} -shm".format(
                kma_path, input[0], target_dir + consensus_name, kma_database_path,
                str(best_template), str(multi_threading), str(bc))
            print(cmd, file=logfile)
            check_shm_kma(kma_path, kma_database_path, cmd, logfile)
        print("# Nanopore mapping completed succesfully", file=logfile)

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

def md5(sequence):
    hash_md5 = hashlib.md5(sequence.encode())
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

def ThreshholdDistanceCheck(distancematrixfile, reference, consensus_name):
    infile = open(distancematrixfile, 'r')
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == reference or line[0] == consensus_name:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == reference or line[0] == consensus_name:
                index = linecount
                secondentry = True
        linecount += 1

def scan_reference_vs_isolate_cge(plasmid_string, allresgenes, virulence_string, header_text, db_dir):

    plasmids_isolate = plasmid_string.split(",")
    amrgenes_isolate = allresgenes.split(",")
    virulencegenes_isolate = virulence_string.split(",")

    #This function checks if an isolate has any unique amrgenes, virulencegenes or plasmids vs the cluster and returns them if any are found
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM isolatetable WHERE header_text = '{}'".format(header_text))
    refdata = c.fetchall()

    print (refdata)

    if refdata != []:
        if refdata[0][0] == None:
            plasmids_reference = []
        else:
            plasmids_reference = refdata[0][0].split(",")
    else:
        plasmids_reference= []

    c.execute("SELECT virulencegenes FROM isolatetable WHERE header_text = '{}'".format(header_text))
    refdata = c.fetchall()
    if refdata != []:
        if refdata[0][0] == None:
            virulencegenes_reference = []
        else:
            virulencegenes_reference = refdata[0][0].split(",")
    else:
        virulencegenes_reference = []

    c.execute("SELECT amrgenes FROM isolatetable WHERE header_text = '{}'".format(header_text))
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
    if new_plasmid_string is not None:
        new_plasmid_string = new_plasmid_string.replace("'", "''")
    if new_virulence_string is not None:
        new_virulence_string = new_virulence_string.replace("'", "''")
    if new_amr_string is not None:
        new_amr_string = new_amr_string.replace("'", "''")



    return new_plasmid_string, new_virulence_string, new_amr_string





def generateFigtree(inputfile, jobid):
    #Figtree doesnt work on laptop

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

def inputAssemblyFunction(assemblyType, inputType, target_dir, input, illumina_name1, illumina_name2, jobid, samplename, kma_path, kma_database_path, entryid, isolatedb, db_dir, associated_species):
    if assemblyType == "illumina":
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
                jobid, input[0], samplename, samplename)
            os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_results", jobid), shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/dockertmp/assembly_results {}.".format(id, target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)

        path = "{}/assembly_results".format(target_dir)
        if os.path.exists(path):
            assembly_result = check_assembly_result(path)
        else:
            assembly_result = False

        if assembly_result:
            # concatenate all reads into one file

            infile = open("{}assembly_results/assembly.fasta".format(target_dir), 'r')
            writefile = open("{}{}_assembled.fasta".format(target_dir, samplename), 'w')  # Adds all contigs to one sequence
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line
            print(">" + samplename, file=writefile)
            print(sequence, file=writefile)
            infile.close()
            writefile.close()

            #Assembly complete

            #Here, prior to indexeing recheck with kma mapping for new reference hit, else add #DEVELOP

            #Before indexing check semaphore for new reference
            result, action = acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
            if result == 'acquired' and action == False:
                cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir,
                                                                         samplename)  # add assembly to references
                os.system(cmd)
                release_semaphore("ipc_index_refdb", db_dir)

            elif result != 'acquired' and action == True:
                result += " : ipc_index_refdb"
                sys.exit(result)
            else:
                sys.exit('A semaphore related issue has occured.')

            conn = sqlite3.connect(isolatedb)
            c = conn.cursor()
            #Here, check and insert amrgenes, virulencegenes, plasmids.
            dbstring = "INSERT INTO referencetable(entryid, header_text) VALUES ('{}', '{}')".format(entryid, associated_species)
            c.execute(dbstring)
            conn.commit()  # Need IPC
            conn.close()

            cmd = "mkdir {}datafiles/isolatefiles/{}".format(db_dir, samplename)
            os.system(cmd)

            cmd = "mkdir {}datafiles/distancematrices/{}".format(db_dir, samplename)
            os.system(cmd)
        else:
            #Fix sql status table and update to falied assembly run.
            sys.exit("Assembly failed")



    elif assemblyType == "nanopore":
        ##docker pull nanozoo/unicycler:0.4.7-0--c0404e6
        print("no template TRUE runnning nanopore assembly")

        cmd = "docker run --name assembly_results{} -v {}:/tmp/{} nanozoo/unicycler:0.4.7-0--c0404e6 unicycler -l /tmp/{} -o /tmp/assembly_results -t 4".format(
            jobid, input[0], samplename, samplename)
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
        writefile = open("{}{}_assembled.fasta".format(target_dir, samplename), 'w')  # Adds all contigs to one sequence
        sequence = ""
        for line in infile:
            if line[0] != ">":
                line = line.rstrip()
                sequence += line
        print(">" + samplename, file=writefile)
        print(sequence, file=writefile)
        infile.close()
        writefile.close()

        # Assembly complete

        result, action = acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
        if result == 'acquired' and action == False:
            cmd = "{} index -t_db {} -i {}{}_assembled.fasta".format(kma_path, kma_database_path, target_dir,
                                                                     samplename)  # add assembly to references
            print (cmd)
            print (cmd)

            print (cmd)

            os.system(cmd)


            release_semaphore("ipc_index_refdb", db_dir)

        elif result != 'acquired' and action == True:
            result += " : ipc_index_refdb"
            sys.exit(result)
        else:
            sys.exit('A semaphore related issue has occured.')

        conn = sqlite3.connect(isolatedb)
        c = conn.cursor()
        dbstring = "INSERT INTO referencetable(entryid, header_text) VALUES('{}', '{}')".format(entryid, associated_species)
        c.execute(dbstring)
        conn.commit()  # Need IPC
        conn.close()


def uniqueNameCheck(db_dir, inputType, total_filenames):
    if inputType == "nanopore":
        inputpath = total_filenames
        samplename = inputpath.split("/")[-1]
    elif inputType == "pe_illumina":
        inputpath = total_filenames.split(" ")[0]
        samplename = inputpath.split("/")[-1]
    elif inputType == "se_illumina":
        inputpath = total_filenames
        samplename = inputpath.split("/")[-1]

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

    c.execute("SELECT * FROM isolatetable WHERE samplename = '{}'".format(samplename))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An isolate sample has the same filename as your input. Please change your input file's name.")

    c.execute("SELECT * FROM referencetable WHERE header_text = '{}'".format(header))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An reference sample has the same filename or header string as your input. Please change your input file's name.")


    conn.close()

def semaphoreInitCheck():
    # Check if an assembly is currently running

    #Mangler, check for value, if 0, ergo assembly quit


    semaphore = posix_ipc.Semaphore("/ipc_index_refdb", posix_ipc.O_CREAT, initial_value=1)
    assembly_semaphore_value = semaphore.value
    if assembly_semaphore_value == 0:
        print ("Another subprocess is currently writing to the reference database")
        try:
            semaphore.acquire(timeout=18000)  # Wait maxium of 5 hours.
            semaphore.release()  # No database writing, clear to go
        except posix_ipc.BusyError as error:
            semaphore.unlink()
            sys.exit("ipc_index_refdb semaphore is jammed. A process waited > 5H to write to the reference database. Run CleanSemaphore.py to wipe all phores")

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
            infile.close()
            return t
        else:
            t = t + 1
    infile.close()


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

def runResFinder(exepath, total_filenames, target_dir, seqType):
    #cmd = "python3 {}resfinder/run_resfinder.py -ifq {} -o {}resfinderResults -b {}resfinder/cge/ncbi-blast-2.10.1+/bin/blastn -acq".format(exepath, total_filenames, target_dir, exepath)
    if seqType == 'nanopore':
        cmd = "python3 {}resfinder/run_resfinder.py -ifq {} -o {}resfinderResults -k {}kma/kma -acq -nano".format(exepath, total_filenames, target_dir, exepath)
        os.system(cmd)
    else:
        cmd = "python3 {}resfinder/run_resfinder.py -ifq {} -o {}resfinderResults -k {}kma/kma -acq".format(exepath,
                                                                                                            total_filenames,
                                                                                                            target_dir,
                                                                                                            exepath)
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

def lastClusterAddition(db_dir, header_text):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT entryid, analysistimestamp FROM isolatetable WHERE header_text = '{}' ORDER BY analysistimestamp DESC".format(header_text)) #Dårlig løsning, ikke skalerbar til >5M isolates
    refdata = c.fetchall()
    conn.close()
    return refdata

def isolate_file_name(db_dir, entryid):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT samplename FROM isolatetable WHERE entryid = '{}'".format(entryid))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0][0]

    return element


def generate_amr_resistance_profile_table(db_dir, entryid, pdf, target_dir, exepath, header_text):

    panel_found = False
    panel_list = []

    genus = header_text.split()[1]
    species = header_text.split()[2]

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
    print ("Opened amr.csv")
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


def compileReportAssembly(target_dir, ID, db_dir, associated_species, exepath):
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

    cmd = "Rscript {}src/quast_tsv_table.R {}".format(exepath, target_dir)
    os.system(cmd)
    run_bandage(target_dir, ID)
    pdf.image("{}quast_table.png".format(target_dir), x=118, y=60, w=pdf.w / 2.7, h=pdf.h / 2.1)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.cell(85, 5, "Contig visualization:", 0, 1, 'L')
    pdf.image("{}contigs.jpg".format(target_dir), x=15, y=70, w=pdf.w / 2.2, h=pdf.h / 2.7)

    pdf.output(target_dir + filename, 'F')


def retrieve_cge_counts(target_dir, ID, db_dir, image_location, header_text, exepath):
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

    c.execute("SELECT plasmids FROM referencetable WHERE header_text = '{}'".format(header_text))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        plasmids_reference = []
    else:
        plasmids_reference = refdata[0][0].split(",")

    c.execute("SELECT virulencegenes FROM referencetable WHERE header_text = '{}'".format(header_text))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        virulencegenes_reference = []
    else:
        virulencegenes_reference = refdata[0][0].split(",")

    c.execute("SELECT amrgenes FROM referencetable WHERE header_text = '{}'".format(header_text))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        amrgenes_reference = []
    else:
        amrgenes_reference = refdata[0][0].split(",")

    conn.close()



    return plasmids_isolate, virulencegenes_isolate, amrgenes_isolate, plasmids_reference, virulencegenes_reference, amrgenes_reference



def mlst_sequence_type(target_dir):
    try:
        with open(target_dir + "mlstresults/data.json") as json_file:
            data = json.load(json_file)
        sequence_type = data['mlst']['results']['sequence_type']
        return sequence_type
    except:
        return "No MLST Found"



def compileReportAlignment(target_dir, ID, db_dir, image_location, header_text, exepath, related_isolates):
    pdf = FPDF()  # A4 (210 by 297 mm)

    filename = "{}_report.pdf".format(ID) #ADD idd
    clusterSize = len(related_isolates)
    latestAddition = lastClusterAddition(db_dir, header_text)
    phenotypes, panel_found, panel_list = generate_amr_resistance_profile_table(db_dir, ID, pdf, target_dir, exepath, header_text)

    ''' First Page '''
    pdf.add_page()
    pdf.image(exepath + "/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, ID, "MOSS analytical report")
    pdf.ln(5)
    file_name = isolate_file_name(db_dir, ID)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "Sample name: {} \n" \
                 "Identified reference: {} \n" \
                 "".format(ID, file_name, header_text)
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(10)

    analysistimestamp = time_of_analysis(db_dir, ID)
    pdf.set_font('Arial', '', 10)
    #Cell here

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

    sequence_type = mlst_sequence_type(target_dir)

    plasmids_isolate, virulencegenes_isolate, amrgenes_isolate, plasmids_reference, virulencegenes_reference, amrgenes_reference = retrieve_cge_counts(target_dir, ID, db_dir, image_location, header_text, exepath)
    textstring = "AMR genes in this sample: {}. \n" \
                 "AMR genes in this cluster: {}. \n" \
                 "Plasmids in this sample: {}. \n" \
                 "Plasmids in this cluster: {}. \n" \
                 "Virulence genes in this sample: {}. \n" \
                 "Virulence genes in this cluster: {}. \n" \
                 "MLST: ST{}. \n" \
                 "".format(len(amrgenes_isolate), len(amrgenes_reference), len(plasmids_isolate), len(plasmids_reference), len(virulencegenes_reference), len(virulencegenes_reference), sequence_type)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)

    #Rsub-script is not called when page is left
    if panel_found:
        cmd = "Rscript {}src/moss_csv_to_frontside_table.R {}".format(exepath, target_dir)
        os.system(cmd)
        time.sleep(35)
        #here the r script does not produce an image #Sub process stops
        pdf.image("{}amr_table.png".format(target_dir), x=90, y=60, w=pdf.w / 1.95, h=pdf.h / 1.75)

    else:
        pdf.cell(85, 5, "Organism was not in annotated panel. The following AMR genes were found:", 0, 1, 'L')
        cmd = "Rscript {}src/moss_csv_to_frontside_table.R {}".format(exepath, target_dir)
        os.system(cmd)
        #subprocess.run(cmd)
        time.sleep(5)

        pdf.image("{}amr_table.png".format(target_dir), x=90, y=60, w=pdf.w / 1.95, h=pdf.h / 1.75)

    pdf.ln(10)

    pdf.set_font('Arial', '', 12)

    ''' Second Page '''
    pdf.add_page()
    pdf.image(exepath + "/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 6.5, h=pdf.h / 6.5)
    create_title(pdf, ID, "Phylogeny results")
    pdf.ln(20)
    pdf.image(image_location, x=10, y=55, w=pdf.w/1.2, h=pdf.h/1.6)


    pdf.output(target_dir + filename, 'F')

def compare_plasmid_isolate_vs_cluster(plasmid_list, header_text, db_dir):
    isolatedb = db_dir + "moss.db"
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM referencetable WHERE header_text = '{}'".format(header_text))
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
    #HERE SOMETHINIG HAPPEND CHECK
    if os.path.isfile(jsoninput):
        with open(jsoninput) as json_file:
            data = json.load(json_file)
        count1 = 0

        virulence_list = []
        for species in data['virulencefinder']['results']:

            for hit in data['virulencefinder']['results'][species]:
                if type(data['virulencefinder']['results'][species][hit]) == dict:
                    print (data['virulencefinder']['results'][species][hit])

                    for gene in data['virulencefinder']['results'][species][hit]:
                        count1 += 1
                        virulence_list.append(gene)
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

def checkAMRrisks(target_dir, entryid, db_dir, header_text, exepath, logfile):
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


    header_textlist = header_text.split()
    speciename = (header_textlist[1] + " " + header_textlist[2]).upper()

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










