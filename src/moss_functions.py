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

import moss_sql as moss_sql
from Bio import Phylo
import matplotlib.pyplot as plt
import pylab
import dataframe_image as dfi


#Utility functions



def derive_phenotype_amr(genes, database, target_dir):
    new_genes = list()
    for item in genes:
        new_genes.append(item.split("_")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/moss/{}/notes.txt".format(database), 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1]].append(line[0])
                else:
                    phenotype[line[1]] = [line[0]]
    csv_line = "Resistance, Genes\n"
    for item in phenotype:
        csv_line += "{},{}\n".format(item, phenotype[item])
    with open(target_dir + "amr.csv", 'w') as writer:
        writer.write(csv_line)
    return phenotype

def derive_phenotype_virulence(genes, database, target_dir):
    new_genes = list()
    for item in genes:
        new_genes.append(item.split(":")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/moss/{}/notes.txt".format(database), 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1].strip()].append(line[0])
                else:
                    phenotype[line[1].strip()] = [line[0]]

    csv_line = "Viruelence, Genes\n"
    for item in phenotype:
        csv_line += "{},{}\n".format(item, phenotype[item])
    with open(target_dir + "virulence.csv", 'w') as writer:
        writer.write(csv_line)
    return phenotype


def push_meta_data_to_sql(metadata_dict, entry_id, config_name):
    sql_cmd = "INSERT INTO metadata_table(entry_id, sample_name, sequencing_method, isolation_source, investigation_type, \
    collection_date, latitude, longitude, city, country) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entry_id, metadata_dict["sample_name"], metadata_dict["sequencing_method"], metadata_dict["isolation_source"], \
                metadata_dict["investigation_type"], metadata_dict["collection_date"], metadata_dict["latitude"], \
                metadata_dict["longitude"], metadata_dict["city"], metadata_dict["country"])
    sql_execute_command(sql_cmd, config_name)

def push_finders_data_sql(target_dir, config_name, entry_id):
    resfinder_hits = parse_kma_res("{}/finders/resfinder.res".format(target_dir))
    virulence_hits = parse_kma_res("{}/finders/virulencefinder.res".format(target_dir))
    plasmid_hits = parse_kma_res("{}/finders/plasmidfinder.res".format(target_dir))
    mlst_type = parse_mlst_result("{}/mlstresults/data.json".format(target_dir))

    sql_cmd = "UPDATE sample_table SET amr_genes=\"{}\", virulence_genes=\"{}\", plasmids=\"{}\", mlst=\"{}\" WHERE entry_id=\"{}\"" \
        .format(",".join(resfinder_hits).replace("'", "''"), ",".join(virulence_hits).replace("'", "''"), \
                ",".join(plasmid_hits).replace("'", "''"), mlst_type, entry_id)
    sql_execute_command(sql_cmd, config_name)

    return resfinder_hits, virulence_hits, plasmid_hits, mlst_type

def parse_mlst_result(filename):
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
        sequence_type = data['mlst']['results']['sequence_type']
        return sequence_type
    except:
        return "Unknown"



def parse_kma_res(filename):
    item_list = list()
    infile = open(filename, 'r')
    for line in infile:
        if line[0] != "#":
            line = line.split('\t')
            item_list.append(line[0])
    return item_list

def kma_finders(arguments, outputname, target_dir, input, database):
    os.system("/opt/moss/kma/kma -i {} -o {}/finders/{} -t_db {} {}".format(input, target_dir, outputname, database, arguments))



def derive_finalized_filenames(input_dir):
    """
    Either, directory have barcode01-barocdeX subdirectories. if so:
        Check number of files. If >1, check combined file. If non, create.
    else:
        evaluate.

    """
    directory_type = None

    sub_directories = os.listdir(input_dir)
    if len(sub_directories) > 1:
        dir_list = list()
        file_list = list()
        for item in sub_directories:
            if os.path.isfile(input_dir + item):
                file_list.append(item)
            elif os.path.isdir(input_dir + item):
                dir_list.append(item)
        if len(dir_list) > 0 and len(file_list) == 0:
            pass
            #Only directoriespass
        elif len(file_list) > 0 and len(dir_list) == 0:
            pass
            #Only files

        elif len(file_list) > 0 and len(dir_list) > 0:
            pass
            #Mix
        #CONTINUE

    else:
        #Check if one fastq
        if os.path.isfile(input_dir + sub_directories[0]):
            if sub_directories[0].endswith('.fastq') or sub_directories[0].endswith('.fastq.gz'):
                #Assume that this one, single fastq file is the whole input.
                return (input_dir + sub_directories[0], "single_input_fastq")
            else:
                sys.exit("The input does not appear to be a fastq file")
        elif os.path.isdir(input_dir + sub_directories[0]):
            if sub_directories[0] != "barcode01":
                sys.exit("The input fastq files given in the metadata sheet are not correct. Please see the documentation at <LINK> for the correct input format.")

    print (sub_directories)

    return ["test", "test2"]


def create_directory_from_dict(dict, path):
    for directory in dict:
        os.system("mkdir {}{}".format(path, directory))
        for subdirectory in dict[directory]:
            os.system("mkdir {}{}/{}".format(path, directory, subdirectory))
    return True

def sql_fetch(string, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    c.execute(string)
    data = c.fetchall()
    conn.close()
    return data

def sql_execute_command(command, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()

def moss_mkfs(config_name, entry_id):
    target_dir = "/opt/moss_db/{}/analysis/{}/".format(config_name, entry_id)
    os.system("mkdir {}".format(target_dir))

def moss_init(config_name, metadata, metadata_headers):
    metadata_dict = prod_metadata_dict(metadata, metadata_headers)
    print (metadata_dict)
    if metadata_dict['ont_type'] == "fast5":
        #TBD
        input = "{}/barcode{}/{}.fastq.gz".format(metadata_dict['file_location'], metadata_dict['barcode_number'])
    else:
        input = metadata_dict['file_location']

    if metadata_dict['latitude'] == '' or metadata_dict['longitude'] == '':
        latitude, longitude = calc_coordinates_from_location(metadata_dict['city'], metadata_dict['country'])
        metadata_dict['latitude'] = latitude
        metadata_dict['longitude'] = longitude

    if input.endswith("fastq.gz"):
        sample_name = input.split("/")[-1][0:-9]
    elif input.endswich("fastq"):
        sample_name = input.split("/")[-1][0:-6]
    else:
        sys.exit("input is not a fastQ file.")
    entry_id = md5(input)

    uniqueNameCheck(input, config_name)

    if input.split("/")[-1][-2:] == "gz":
        c_name = input.split("/")[-1][:-2]
    else:
        c_name = input.split("/")[-1][:10]

    ref_db = "/opt/moss_db/{}/REFDB.ATG".format(config_name)
    target_dir = "/opt/moss_db/{}/analysis/{}/".format(config_name, entry_id)

    push_meta_data_to_sql(metadata_dict, entry_id, config_name)

    return config_name, metadata_dict, input, sample_name, entry_id, target_dir, ref_db, c_name


def get_kma_template_number(reference_header_text, config_name):
    infile = open("/opt/moss_db/{}/REFDB.ATG.name".format(config_name), 'r')
    t = 1
    number = 0
    for line in infile:
        if reference_header_text in line:
            infile.close()
            return t
        t += 1
    infile.close()
    return t

def make_phytree_output_folder(config_name, target_dir, isolate_list, reference_header_text):
    cmd = "mkdir {}/phytree_output".format(target_dir)
    os.system(cmd)

    for item in isolate_list:
        path = "/opt/moss_db/{}/consensus_sequences/{}".format(config_name, item)
        cmd = "cp {} {}/phytree_output/.".format(path, target_dir)
        os.system(cmd)

    number = get_kma_template_number(reference_header_text, config_name)
    header_name = reference_header_text.split()[0]
    cmd = "/opt/moss/kma/kma seq2fasta -t_db /opt/moss_db/{}/REFDB.ATG -seqs {} > {}/phytree_output/{}.fsa".format(config_name, number, target_dir, header_name)
    os.system(cmd)

    cmd = "cp {}*_consensus.fsa {}phytree_output/.".format(target_dir, target_dir)
    os.system(cmd)

def create_phylo_tree(target_dir):
    tree = Phylo.read("{}phytree_output/tree.newick".format(target_dir), 'newick')
    Phylo.draw(tree, do_show=False)
    pylab.savefig("{}phytree_output/tree.png".format(target_dir))
    image_location = "{}/phytree_output/tree.png".format(target_dir)
    return image_location



def moss_shortcut_init():
    outfile = open('/opt/moss/src/moss', 'w')
    print ("#!/usr/bin/env bash", file = outfile)
    print ("echo \'HELLO THERE\'", file = outfile)
    outfile.close()
    cmd = "mv /opt/moss/src/moss ~/bin/."
    os.system(cmd)
    cmd = "chmod a+x ~/bin/moss"
    os.system(cmd)

def init_insert_reference_table(config_name):
    infile = open(config_name + "REFDB.ATG.name", 'r')
    t = 1
    conn = sqlite3.connect(config_name + 'moss.db')
    c = conn.cursor()
    ids = list()

    for line in infile:
        line = line.rstrip()
        cmd = "/opt/moss/kma/kma seq2fasta -t_db {}/REFDB.ATG -seqs {}".format(config_name, t)
        proc = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0].decode()
        reference_header_text = output.split("\n")[0][1:]
        sequence = output.split("\n")[1]
        entry_id = md5(sequence)
        #TMP SOLUTION TO AVOID ENTRYCLASHES:
        if entry_id not in ids:
            dbstring = "INSERT INTO reference_table(entry_id, reference_header_text) VALUES('{}', '{}')".format(entry_id, reference_header_text.replace("'", "''"))
            ids.append(entry_id)
            c.execute(dbstring)

        t += 1
    conn.commit()
    conn.close()

def check_assembly_result(path):

    return True

def run_assembly(entry_id, config_name, sample_name, target_dir, input, reference_header_text, associated_species):
    sql_cmd = "UPDATE sample_table SET reference_id=\"{}\" WHERE entry_id=\"{}\"" \
        .format("reference", entry_id)
    sql_execute_command(sql_cmd, config_name)
    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Flye Assembly", "reference", "4", "5", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    sql_execute_command(sql_cmd, config_name)
    flye_assembly(entry_id, config_name, sample_name, target_dir, input, reference_header_text)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF report", "reference", "5", "5", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    sql_execute_command(sql_cmd, config_name)

    #compileReportAssembly(target_dir, entry_id, config_name, associated_species) #Look at the TBD

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Assembly pipeline completed", "reference", "5", "5", "Completed", str(datetime.datetime.now())[0:-7], entry_id)
    sql_execute_command(sql_cmd, config_name)
    sys.exit("No template was found, so input was added to references.")

def init_moss_variables(config_name, ):
    referenceSyncFile = config_name + "syncFiles/referenceSync.json"
    isolateSyncFile = config_name + "syncFiles/isolateSync.json"
    return "/opt/moss/kma/kma"

def update_pip_dependencies():
    cmd = "python3 -m pip install --upgrade fpdf"
    os.system(cmd)
    cmd = "python3 -m pip install --upgrade tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    pip_list = ["geocoder", "pandas", "geopy", "Nominatim"]
    for item in pip_list:
        cmd = "pip install --upgrade {}".format(item)
        os.system(cmd)


def update_moss_dependencies(laptop, update_list, force):
    if force:
        if laptop:
            print ("laptop FORCE TBD")
        else:
            cmd = "cd /opt/moss/"
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
                cmd = "cd /opt/moss/"
                os.system(cmd)
                cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
                os.system(cmd)
            if "ccphylo" in update_list:
                cmd = "cd /opt/moss/"
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

def varify_all_dependencies(laptop):
    update_list = []
    if not varify_tool("/opt/moss/kma/kma -v", '1.3.24', -8, -2):#KMA, expected: KMA-1.3.24+
        update_list.append("kma")
    if not varify_tool("/opt/moss/ccphylo/ccphylo -v", '0.5.3', -6, -1): #ccphylo, expected: CCPhylo-0.5.3
        update_list.append("ccphylo")
    if not varify_tool("docker -v", '20.10.8', 15, 22): #docker, Docker version 20.10.8, build 3967b7d28e
        update_list.append("docker")
    if not laptop:
        pass #Test CUDA
        #ont-guppy test
    if not varify_tool("R --version", '4.0.0', 10, 15): #R
        update_list.append("r")
    if not varify_tool("npm -v", '7.0.0', 0, -1): #npm 7.21.1
        update_list.append("npm")
    if not varify_tool("pip --version", '21.0.0', 4, 10): #pip, pip 21.3.1 from /user/etc/etc
        update_list.append("python3-pip")
    if not varify_tool("conda --version", '4.0.0', 6, -1): #conda, conda 4.10.1
        update_list.append("conda")
    return update_list




def run_mlst(input, target_dir, reference_header_text):

    specie = reference_header_text.split()[1].lower() + " " + reference_header_text.split()[2].lower() #Make broader implementation here - fx "ecoli" is for e.coli mlst - how does that worK?

    mlst_dict = dict()
    infile = open("/opt/moss/mlst/mlst_db/config", 'r')
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
        cmd = "python3 /opt/moss/mlst/mlst.py -i {} -o {}mlstresults -mp /opt/moss/kma/kma -p /opt/moss/mlst/mlst_db/ -s {} -nano".format(input, target_dir, mlst_dict[specie])
        os.system(cmd)
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


#def check_shm_kma("/opt/moss/kma/kma", kma_database_path, cmd):
#    try: #Check if KMA db in shm
#        cmd_stdout = check_output(cmd, stderr=STDOUT, shell=True).decode()
#    except Exception as e:
#        os.system("{}_shm -t_db {}".format("/opt/moss/kma/kma", kma_database_path)) #Loads DB
#        os.system(cmd)
#        return True

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

def kma_mapping(target_dir,  input, config_name):
    os.system("/opt/moss/kma/kma -i {} -o {}kma_mapping -t_db /opt/moss_db/{}/REFDB.ATG -ID 0 -nf -mem_mode -sasm -ef".format(input, target_dir, config_name))

    try:
        template_number_score = 0
        reference_header_text = None
        infile = open("{}kma_mapping.res".format(target_dir), 'r')
        for line in infile:
            line = line.rstrip()
            line = line.split("\t")
            if line[0][0] != "#":
                if float(line[1]) > template_number_score:
                    template_number_score = float(line[1])
                    reference_header_text = line[0]
        template_number = findTemplateNumber(config_name, reference_header_text)
        if template_number_score == 0:
            return (0, 1, "", template_number) #template_search_result = 0 (index 1) its a hit. Here its not.
        else:
            return (template_number_score, 0, reference_header_text, template_number)
    #If no match are found, the sample will be defined as a new reference.
    except IndexError as error:
        print(
            "None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.")

        # Perform assembly based on input
        template_search_result = False
        print("FoundnoTemplate")
        return (0, 1, "", "") #template_search_result = 0 means no result found
    ###

def nanopore_alignment(input, template_number, target_dir, consensus_name, config_name):
    result, action = acquire_semaphore("ipc_index_refdb", config_name, 1, 7200)
    if result == 'acquired' and action == False:
        release_semaphore("ipc_index_refdb", config_name)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb, didn't map due to running assembly"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')
    cmd = "/opt/moss/kma/kma -i {} -o {} -t_db /opt/moss_db/{}/REFDB.ATG -mp 20 -1t1 -dense -nf -vcf -ref_fsa -ca -bcNano -Mt1 {} -t 8 -bc 0.9"\
        .format(input, target_dir + consensus_name, config_name, str(template_number))
    os.system(cmd)

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

def md5(sequence):
    hash_md5 = hashlib.md5(sequence.encode())
    return hash_md5.hexdigest()

def claim_semaphore(semaphore, config_name, value):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    dbstring = "UPDATE ipc_table SET {} = '{}' WHERE ipc = '{}'".format(semaphore, int(value)-1, 'IPC')
    c.execute(dbstring)
    conn.commit()
    conn.close()

def acquire_semaphore(semaphore, config_name, expected, time_limit):

    running_time = 0
    result = ""
    action = False
    semaphore_status = False
    value = check_sql_semaphore_value(semaphore, config_name)
    print ("Semapore value : " + str(value))
    if value != expected:
        while value != expected:
            print (running_time)
            time.sleep(10)
            running_time += 10
            value = check_sql_semaphore_value(semaphore, config_name)
            if running_time >= time_limit:
                result = "Running time exceeded the 7200, a semaphore is likely jammed"
                action = True
                break
        claim_semaphore(semaphore, config_name, value)
        result = "acquired"
    else:
        claim_semaphore(semaphore, config_name, value)
        result = "acquired"

    return result, action

def reset_semaphore(semaphore, config_name):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    dbstring = "UPDATE ipc_table SET {} = '{}'".format(semaphore, 1)
    c.execute(dbstring)
    conn.commit()
    conn.close()

def release_semaphore(semaphore, config_name):

    value = check_sql_semaphore_value(semaphore, config_name)
    if value > 1:
        sys.exit("Semaphores are jammed. Contact Author, this is an unexpected issue.")

    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()
    dbstring = "UPDATE ipc_table SET {} = '{}'".format(semaphore, int(value) + 1)
    c.execute(dbstring)
    conn.commit()
    conn.close()

def check_sql_semaphore_value(semaphore, config_name):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)

    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT {} FROM ipc_table".format(semaphore))
    refdata = c.fetchall()
    conn.close()

    return int(refdata[0][0])

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

def flye_assembly(entry_id, config_name, sample_name, target_dir, input, reference_header_text):

    cmd = "docker run --name assembly_{} -v {}:/tmp/{} staphb/flye flye -o /tmp/assembly_results --threads 8 --nano-raw /tmp/{}".format(
        entry_id, input, input.split("/")[-1], input.split("/")[-1])
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_", entry_id), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/assembly_results {}.".format(id, target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    # Concatenate contigs
    infile = open("{}assembly_results/assembly.fasta".format(target_dir), 'r')
    writefile = open("{}{}_assembly.fasta".format(target_dir, sample_name),
                     'w')  # Adds all contigs to one sequence, thus creating a draft genome.
    sequence = ""
    for line in infile:
        if line[0] != ">":
            line = line.rstrip()
            sequence += line
    new_header_text = ">Assembly of raw reads, closest reference was : " + reference_header_text[1:]
    print(new_header_text, file=writefile)
    print(sequence, file=writefile)
    infile.close()
    writefile.close()

    # Assembly complete

    result, action = acquire_semaphore("ipc_index_refdb", config_name, 1, 7200)
    if result == 'acquired' and action == False:
        cmd = "{} index -t_db {} -i {}{}_assembly.fasta".format("/opt/moss/kma/kma", "/opt/moss_db/{}/REFDB.ATG".format(config_name), target_dir,
                                                                 sample_name)  # add assembly to references

        os.system(cmd)

        release_semaphore("ipc_index_refdb", config_name)

    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured.')
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    dbstring = "INSERT INTO reference_table(entry_id, reference_header_text) VALUES('{}', '{}')".format(entry_id, new_header_text[1:])
    c.execute(dbstring)
    conn.commit()
    conn.close()


def uniqueNameCheck(input, config_name):
    sample_name = input.split("/")[-1]

    if input[-3:] == ".gz":
        infile = gzip.open(input, 'rb')
        first_line = infile.readline().rstrip().decode("utf8")
    else:
        infile = open(input, 'r')
        first_line = infile.readline().rstrip()

    header = first_line[1:]
    if first_line[0] == ">": #Reference
        print (header)
        if " " in header:
            accession = header.split(" ")[0]
        else:
            accession = header
    else:
        accession = input.split("/")[-1]

    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()

    c.execute("SELECT * FROM sample_table WHERE sample_name = '{}'".format(sample_name))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An isolate sample has the same filename as your input. Please change your input file's name.")

    c.execute("SELECT * FROM reference_table WHERE reference_header_text = '{}'".format(header))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit("An reference sample has the same filename or header string as your input. Please change your input file's name.")

    conn.close()

def findTemplateNumber(config_name, name):
    if name == None:
        return ""
    infile = open("/opt/moss_db/{}/REFDB.ATG.name".format(config_name), 'r')
    t = 1
    for line in infile:
        if line.rstrip() == name:
            infile.close()
            return t
        else:
            t = t + 1
    infile.close()

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

def lastClusterAddition(config_name, reference_header_text):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT entry_id, analysistimestamp FROM sample_table WHERE reference_header_text = '{}' ORDER BY analysistimestamp DESC".format(reference_header_text)) #Dårlig løsning, ikke skalerbar til >5M isolates
    refdata = c.fetchall()
    conn.close()
    return refdata

def isolate_file_name(config_name, entry_id):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT sample_name FROM sample_table WHERE entry_id = '{}'".format(entry_id))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0][0]

    return element




def run_bandage(target_dir, jobid):
    #TBD run bandage in assembly func
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


def compileReportAssembly(target_dir, ID, config_name, associated_species):
    #QA checks?
    #Quast?

    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(ID)  # ADD idd

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, ID, "MOSS analytical report")
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "sample_name: {} \n" \
                 "No reference cluster was identified. \n" \
                 "".format(ID, associated_species) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    run_quast(target_dir, ID)

    df = pd.read_csv(target_dir + "quast_output/report.tsv", sep='\t')
    print(df)

    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    dfi.export(df_styled, target_dir + "quast_table.png")
    pdf.image("{}quast_table.png".format(target_dir), x=10, y=40, w=pdf.w / 1.5, h=pdf.h / 1.75)
    run_bandage(target_dir, ID)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.cell(85, 5, "Contig visualization:", 0, 1, 'L')
    pdf.image("{}contigs.jpg".format(target_dir), x=15, y=70, w=pdf.w / 2.2, h=pdf.h / 2.7)

    pdf.output(target_dir + filename, 'F')


def retrieve_cge_counts(target_dir, ID, config_name, image_location, reference_header_text):
    isolatedb = "/opt/moss_db/{}/moss.db".format(config_name)
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT plasmids FROM sample_table WHERE entry_id = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        plasmids_isolate = []
    else:
        plasmids_isolate = refdata[0][0].split(",")

    c.execute("SELECT virulencegenes FROM sample_table WHERE entry_id = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        virulencegenes_isolate = []
    else:
        virulencegenes_isolate = refdata[0][0].split(",")

    c.execute("SELECT amrgenes FROM sample_table WHERE entry_id = '{}'".format(ID))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        amrgenes_isolate = []
    else:
        amrgenes_isolate = refdata[0][0].split(",")

    c.execute("SELECT plasmids FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        plasmids_reference = []
    else:
        plasmids_reference = refdata[0][0].split(",")

    c.execute("SELECT virulencegenes FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text))
    refdata = c.fetchall()

    if refdata[0][0] == None:
        virulencegenes_reference = []
    else:
        virulencegenes_reference = refdata[0][0].split(",")

    c.execute("SELECT amrgenes FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text))
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



def compileReportAlignment(target_dir, entry_id, config_name, reference_header_text, related_isolates, resfinder_hits, virulence_hits, plasmid_hits, mlst_type, sample_name):
    pdf = FPDF()  # A4 (210 by 297 mm)

    filename = "{}_report.pdf".format(entry_id) #ADD idd
    clusterSize = len(related_isolates)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, entry_id, "MOSS analytical report")
    pdf.ln(5)
    file_name = isolate_file_name(config_name, entry_id)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "sample_name: {} \n" \
                 "Identified reference: {} \n" \
                 "".format(entry_id, sample_name, reference_header_text)
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(10)
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
                 "".format(clusterSize)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)
    pdf.set_text_color(51, 153, 255)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "CGE results: ", 0, 1, 'L')

    textstring = "AMR genes in this sample: {}. \n" \
                 "Plasmids in this sample: {}. \n" \
                 "Virulence genes in this sample: {}. \n" \
                 "MLST: ST{}. \n" \
                 "".format(len(resfinder_hits), len(plasmid_hits), len(virulence_hits), mlst_type)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, entry_id, "AMR Results")
    pdf.ln(40)

    pdf.ln(10)

    pdf.set_font('Arial', '', 12)

    amr_pheno = derive_phenotype_amr(resfinder_hits, "resfinder_db", target_dir)
    virulence_pheno = derive_phenotype_virulence(virulence_hits, "virulencefinder_db", target_dir)

    textstring = "{} {}".format(amr_pheno, virulence_pheno)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)



    df = pd.read_csv(target_dir + "amr.csv")

    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    dfi.export(df_styled, target_dir + "amr_table.png")
    pdf.image("{}amr_table.png".format(target_dir), x=10, y=40, w=pdf.w / 1.5, h=pdf.h / 1.75)

    df = pd.read_csv(target_dir + "virulence.csv")

    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    dfi.export(df_styled, target_dir + "virulence_table.png")
    pdf.image("{}virulence_table.png".format(target_dir), x=10, y=140, w=pdf.w / 1.5, h=pdf.h / 1.75)


    pdf.ln(10)

    pdf.set_font('Arial', '', 12)
    """
    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 6.5, h=pdf.h / 6.5)
    create_title(pdf, ID, "Phylogeny results")
    pdf.ln(20)
    pdf.image(image_location, x=10, y=55, w=pdf.w/1.2, h=pdf.h/1.6)
    """

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

def virulence_data_for_report(jsoninput, target_dir):
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








