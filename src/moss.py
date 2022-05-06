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
parser.add_argument("-config_name", action="store", type=str, default = "", dest="config_name", help="config_name.")
parser.add_argument('-version', action='version', version='MOSS 1.0.0')
parser.add_argument("-metadata", action="store", dest="metadata", default = "", help="metadata")
parser.add_argument("-metadata_headers", action="store", dest="metadata_headers", default = "", help="metadata_headers")

args = parser.parse_args()

def moss_pipeline(config_name, metadata, metadata_headers):
    start_time = datetime.datetime.now()

    config_name, metadata_dict, input, sample_name, entryid, target_dir, ref_db, c_name = moss.moss_init(config_name, metadata, metadata_headers)
    moss.sql_execute_command("INSERT INTO sample_table(entryid, sample_name, reference_id, amr_genes, virulence_genes, plasmids) VALUES('{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entryid, sample_name, "", "", "", "", ""), config_name)

    moss.sql_execute_command("INSERT INTO status_table(entryid, status, type, current_stage, final_stage, result, time_stamp) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
        entryid, "Initializing", "Not determined", "1", "10", "Running", str(datetime.datetime.now())[0:-7],), config_name)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entryid=\"{}\""\
                             .format("CGE finders", "Not Determined", "2", "10", "Running", str(datetime.datetime.now())[0:-7], entryid)
    moss.sql_execute_command(sql_cmd, config_name)

    #moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CGE finders", "Not Determined", "2", "10", "Running", config_name), config_name)


    moss.moss_mkfs(config_name, entryid)

    #TBC FOR ALL FINDERS INSERT RELEVANT DATA INTO SQL
    # #add argument and check function TBD
    os.system("mkdir {}/finders".format(target_dir))
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "resfinder", target_dir, input, "/opt/moss/resfinder_db/all")
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "virulencefinder", target_dir, input, "/opt/moss/virulencefinder_db/all")
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "resfinder_db", target_dir, input, "/opt/moss/resfinder_db/all")

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entryid=\"{}\"" \
        .format("KMA Mapping", "Not Determined", "3", "10", "Running", str(datetime.datetime.now())[0:-7], entryid)
    moss.sql_execute_command(sql_cmd, config_name)

    #Rewrite this horrible kma_mapping function. Should be way simpler.
    template_score, template_search_result, reference_header_text, template_number = moss.kma_mapping(target_dir, input, config_name)

    associated_species = "{} - assembly from ID: {}".format(reference_header_text, entryid)

    mlst_result = moss.run_mlst(input, target_dir, reference_header_text) #TBD mlst_result used for what?

    if template_search_result == 1: #1 means error, thus no template found
        #Implement flye TBD later.
        moss.run_assembly(entryid, config_name, sample_name, target_dir, input, reference_header_text,
                          associated_species)
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "IPC check", "Alignment", "4", "10", "Running", config_name), config_name)

    #Semaphores should be managed better tbh. Function within function?
    result, action = moss.acquire_semaphore("ipc_index_refdb", config_name, 1, 7200)
    if result == 'acquired' and action == False:
        moss.release_semaphore("ipc_index_refdb", config_name)
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

    consensus_name = "{}_{}_consensus".format(c_name, templateaccesion)

    moss.nanopore_alignment(input, template_number, target_dir, consensus_name, config_name)

    referenceid = moss.sql_fetch("SELECT entryid FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text), config_name)[0][0]

    moss.sql_execute_command("UPDATE sample_table SET referenceid = '{}' WHERE entryid = '{}'".format(referenceid, entryid), config_name)

    sys.exit("TEST HREE")
    #Managed in function when consensus in created ffs.
    cmd = "cp {}{}.fsa {}/consensus_sequences/{}.fsa".format(target_dir, consensus_name, config_name, consensus_name)
    os.system(cmd)

    #Generic SQL query
    moss.sql_execute_command("UPDATE sample_table SET consensus_name = '{}.fsa' WHERE entryid = '{}'".format(consensus_name, entryid), config_name)
    related_isolates = moss.sql_fetch("SELECT consensus_name FROM sample_table WHERE referenceid = '{}'".format(referenceid), config_name)[0][0].split(",")

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CCphylo", "Alignment", "5", "10", "Running", config_name), config_name)


    #Fine, but can we include add ccphylo related in one function?
    moss.make_phytree_output_folder(config_name, target_dir, related_isolates, reference_header_text)

    #Why is cc phylo not in a function?
    cmd = "/opt/moss/ccphylo/ccphylo dist -i {}/phytree_output/* -r \"{}\" -mc 0.01 -nm 0 -o {}/phytree_output/distance_matrix".format(target_dir, reference_header_text, target_dir)

    if prune_distance != 0 :
        cmd += " -pr {}".format(prune_distance)
    os.system(cmd)


    # Check if acceptable snp distance
    distance = moss.ThreshholdDistanceCheck("{}/phytree_output/distance_matrix".format(target_dir), reference_header_text.split()[0]+".fsa", consensus_name+".fsa")
    #Print in function ffs

    if distance > 300: #SNP distance
        #No associated species
        associated_species = "{} - assembly from ID: {}".format(reference_header_text, entryid)
        moss.run_assembly(entryid, config_name, sample_name, target_dir, input, reference_header_text,
                          associated_species)

    #generic sql query
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Distance Matrix", "Alignment", "6", "10", "Running", config_name), config_name)

    #ccphylo in function
    cmd = "/opt/moss/ccphylo/ccphylo tree -i {}/phytree_output/distance_matrix -o {}/phytree_output/tree.newick".format(target_dir, target_dir)
    os.system(cmd)

    #Include all of the below in alignment_related_function
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Phylo Tree imaging", "Alignment", "7", "10", "Running", config_name), config_name)


    image_location = moss.create_phylo_tree(config_name, reference_header_text, target_dir)

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Database updating", "Alignment", "8", "10", "Running", config_name), config_name)

    #moss_sql.update_reference_table(entryid, None, None, None, reference_header_text, config_name)

    moss.sql_execute_command("INSERT INTO amr_table(entryid, sample_name, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(entryid, sample_name, str(datetime.datetime.now())[0:-7], allresgenes.replace("'", "''"), amrinfo.replace("'", "''"), reference_header_text, riskcategory.replace("'", "''"), warning.replace("'", "''")), config_name)

    moss.sql_execute_command("UPDATE sample_table SET {}, {}, {}, {}, {} WHERE {}".format(entryid, reference_header_text, sample_name, plasmid_string.replace("'", "''"), allresgenes.replace(", ", ",").replace("'", "''"), virulence_string.replace("'", "''")), config_name)

    entries, values = moss.sql_string_metadata(metadata_dict)

    moss.sql_execute_command("INSERT INTO metadata_table(entryid, {}) VALUES('{}', {})".format(entries, entryid.replace("'", "''"), values), config_name)

    new_plasmid_string, new_virulence_string, new_amr_string = moss.scan_reference_vs_isolate_cge(plasmid_string, allresgenes.replace(", ", ","), virulence_string, reference_header_text, config_name)

    #Get ride of these strings. Make relational tables for genes too.

    #moss.update_reference_table(entryid, new_amr_string, new_virulence_string, new_plasmid_string, reference_header_text, config_name)

    end_time = datetime.datetime.now()
    run_time = end_time - start_time

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Outbreak Finder", "Alignment", "9", "10", "Running", config_name), config_name)

    #Outbreak_finder wtf? really?
    cmd = "python3 /opt/moss/src/outbreak_finder.py -config_name {}".format(config_name) #WTF TBD
    os.system(cmd)

    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Running", config_name), config_name)

    #Still fails here for multiple non-sync analyses
    #Both alignment report and assembly is fuckly. Fix it.
    moss.compileReportAlignment(target_dir, entryid, config_name, image_location, reference_header_text, related_isolates) #No report compiled for assemblies! Look into it! #TBD
    moss.sql_execute_command("UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Finished", config_name), config_name)


def main():
    moss_pipeline(args.config_name, args.metadata, args.metadata_headers)


if __name__== "__main__":
  main()
