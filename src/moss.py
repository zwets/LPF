#!/usr/bin/env python3

# Copyright (c) 2021, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#
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

import moss_sql as moss_sql
import json
import datetime
import threading
import geocoder

#Note: these parser arguments are NOT meant to be user friendly as terminal commands. They are built to be automatically called from the ELectron Client.
parser = argparse.ArgumentParser(description='.')
parser.add_argument("-configname", action="store", type=str, default = "", dest="configname", help="configname.")
parser.add_argument('-version', action='version', version='MOSS 1.0.0')
parser.add_argument("-metadata", action="store", dest="metadata", default = "", help="metadata")
parser.add_argument("-metadata_headers", action="store", dest="metadata_headers", default = "", help="metadata_headers")

args = parser.parse_args()

jobid = random.randint(1,100000000)

def moss_pipeline(configname, metadata, metadata_headers):
    start_time = datetime.datetime.now()

    configname, metadata_dict, input, samplename, entryid, target_dir, ref_db = moss.moss_init(configname, metadata, metadata_headers)
    moss.sql_execute_command("INSERT INTO isolate_table(entryid, samplename, header_text, analysistimestamp, samplingtimestamp, amrgenes, virulencegenes, plasmids, consensus_name, referenceid) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entryid, samplename, "", str(datetime.datetime.now())[0:-7], metadata_dict["collection date"], "", "", "", "", ""), configname)

    moss.sql_execute_command("INSERT INTO status_table(entryid, status, type, current_stage, final_stage, result, time_stamp) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
        entryid, "Initializing", "Not determined", "1", "10", "Running", str(datetime.datetime.now())[0:-7],), configname)

    print("UPDATE status_table SET entryid={}, status={}, type={}, current_stage={}, final_stage={}, result={}, time_stamp=WHERE {}" \
        .format(entryid, "CGE finders", "Not Determined", "2", "10", "Running", str(datetime.datetime.now())[0:-7]))

    moss.sql_execute_command("UPDATE status_table SET entryid={}, status={}, type={}, current_stage={}, final_stage={}, result={}, time_stamp=WHERE {}"\
                             .format(entryid, "CGE finders", "Not Determined", "2", "10", "Running", str(datetime.datetime.now())[0:-7]), configname)

    #moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CGE finders", "Not Determined", "2", "10", "Running", configname), configname)


    moss.moss_mkfs(configname, entryid)

    #Make moss pip lib for practice and future work. Dont use print, but use linux concat to not have to open file the entirety.

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CGE finders", "Not Determined", "2", "10", "Running", configname), configname)
    sys.exit("Pre finders test")

    #TBC FOR ALL FINDERS INSERT RELEVANT DATA INTO SQL
    # #add argument and check function TBD
    kma_finders("", configname, entryid, input, "/opt/moss/resfinder_db/all")
    kma_finders("", configname, entryid, input, "/opt/moss/virulencefinder_db/all")
    kma_finders("", configname, entryid, input, "/opt/moss/resfinder_db/all")

    sys.exit("Pre mapping test")

    #Rewrite this horrible kma_mapping function. Should be way simpler.
    template_score, template_search_result, reference_header_text = moss.kma_mapping(target_dir, input, configname)

    #check if mlst work TBD
    mlst_result = moss.run_mlst(input, target_dir, reference_header_text)

    #Genertic SQL query
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "KMA Mapping", "Not Determined", "3", "10", "Running", configname), configname)

    sys.exit("TEST")
    #This should be done during kma mapping! #TBD
    best_template = moss.findTemplateNumber(configname, reference_header_text)

    if template_search_result == 1: #1 means error, thus no template found
        #Implement flye
        moss.run_assembly(entryid, configname, samplename, assemblyType, inputType, target_dir, input, illumina_name1,
                          illumina_name2, jobid, exepath, kma_database_path, start_time)

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "IPC check", "Alignment", "4", "10", "Running", configname), configname)

    #Semaphores should be managed better tbh. Function within function?
    result, action = moss.acquire_semaphore("ipc_index_refdb", configname, 1, 7200)
    if result == 'acquired' and action == False:
        moss.release_semaphore("ipc_index_refdb", configname)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured. ipc_index_refdb update')

    #Dont manage SQL compatibility in mainscript. def variables earlier or in functions and return.
    if " " in reference_header_text:
        templateaccesion = reference_header_text.split(" ")[0]
    else:
        templateaccesion = reference_header_text

    #WTF here, managed  variablenames earlier, in functions or not at all!
    if input[0].split("/")[-1][-2:] == "gz":
        c_name = input[0].split("/")[-1][:-2]
    else:
        c_name = input[0].split("/")[-1][:10]

    #Again, see above
    consensus_name = "{}_{}_consensus".format(c_name, templateaccesion)

    moss.nanopore_alignment(input, best_template, target_dir, kma_database_path,  multi_threading, bc, exepath + "kma/kma", templateaccesion, configname, laptop, consensus_name)

    referenceid = moss.sql_fetch("SELECT entryid FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text), configname)[0][0]

    moss.sql_execute_command("UPDATE isolate_table SET referenceid = '{}' WHERE entryid = '{}'".format(referenceid, entryid), configname)

    #Managed in function when consensus in created ffs.
    cmd = "cp {}{}.fsa {}/consensus_sequences/{}.fsa".format(target_dir, consensus_name, configname, consensus_name)
    os.system(cmd)

    #Generic SQL query
    moss.sql_execute_command("UPDATE isolate_table SET consensus_name = '{}.fsa' WHERE entryid = '{}'".format(consensus_name, entryid), configname)
    related_isolates = moss.sql_fetch("SELECT consensus_name FROM isolate_table WHERE referenceid = '{}'".format(referenceid), configname)[0][0].split(",")

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CCphylo", "Alignment", "5", "10", "Running", configname), configname)


    #Fine, but can we include add ccphylo related in one function?
    moss.make_phytree_output_folder(configname, target_dir, related_isolates, exepath, reference_header_text)

    #Why is cc phylo not in a function?
    cmd = "{} dist -i {}/phytree_output/* -r \"{}\" -mc 0.01 -nm 0 -o {}/phytree_output/distance_matrix".format(exepath + "ccphylo/ccphylo", target_dir, reference_header_text, target_dir)

    if prune_distance != 0 :
        cmd += " -pr {}".format(prune_distance)
    os.system(cmd)


    # Check if acceptable snp distance
    distance = moss.ThreshholdDistanceCheck("{}/phytree_output/distance_matrix".format(target_dir), reference_header_text.split()[0]+".fsa", consensus_name+".fsa")
    #Print in function ffs

    if distance > 300: #SNP distance
        #No associated species
        reference_header_text = reference_header_text.split()
        associated_species = "{} {} assembly from ID: {}, SNP distance from best verified reference: {}".format(reference_header_text[1], reference_header_text[2], entryid, distance)
        moss.run_assembly(entryid, configname, samplename, assemblyType, inputType, target_dir, input, illumina_name1,
                          illumina_name2, jobid, exepath, kma_database_path, start_time,  associated_species)
    #generic sql query
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Distance Matrix", "Alignment", "6", "10", "Running", configname), configname)

    #ccphylo in function
    cmd = "{}ccphylo/ccphylo tree -i {}/phytree_output/distance_matrix -o {}/phytree_output/tree.newick".format(exepath, target_dir, target_dir)
    os.system(cmd)

    #Include all of the below in alignment_related_function
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Phylo Tree imaging", "Alignment", "7", "10", "Running", configname), configname)


    image_location = moss.create_phylo_tree(configname, reference_header_text, target_dir)

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Database updating", "Alignment", "8", "10", "Running", configname), configname)

    #moss_sql.update_reference_table(entryid, None, None, None, reference_header_text, configname)

    moss.sql_execute_command("INSERT INTO amr_table(entryid, samplename, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(entryid, samplename, str(datetime.datetime.now())[0:-7], allresgenes.replace("'", "''"), amrinfo.replace("'", "''"), reference_header_text, riskcategory.replace("'", "''"), warning.replace("'", "''")), configname)

    moss.sql_execute_command("UPDATE isolate_table SET {}, {}, {}, {}, {} WHERE {}".format(entryid, reference_header_text, samplename, plasmid_string.replace("'", "''"), allresgenes.replace(", ", ",").replace("'", "''"), virulence_string.replace("'", "''")), configname)

    entries, values = moss.sql_string_metadata(metadata_dict)

    moss.sql_execute_command("INSERT INTO metadata_table(entryid, {}) VALUES('{}', {})".format(entries, entryid.replace("'", "''"), values), configname)

    new_plasmid_string, new_virulence_string, new_amr_string = moss.scan_reference_vs_isolate_cge(plasmid_string, allresgenes.replace(", ", ","), virulence_string, reference_header_text, configname)

    #Get ride of these strings. Make relational tables for genes too.

    moss.update_reference_table(entryid, new_amr_string, new_virulence_string, new_plasmid_string, reference_header_text, configname)

    end_time = datetime.datetime.now()
    run_time = end_time - start_time

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Outbreak Finder", "Alignment", "9", "10", "Running", configname), configname)

    #Outbreak_finder wtf? really?
    cmd = "python3 {}src/outbreak_finder.py -configname {}".format(exepath, configname) #WTF TBD
    os.system(cmd)

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Running", configname), configname)

    #Still fails here for multiple non-sync analyses
    #Both alignment report and assembly is fuckly. Fix it.
    moss.compileReportAlignment(target_dir, entryid, configname, image_location, reference_header_text, exepath, related_isolates) #No report compiled for assemblies! Look into it! #TBD
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Finished", configname), configname)


def main():
    moss_pipeline(args.configname, args.metadata, args.metadata_headers)


if __name__== "__main__":
  main()
