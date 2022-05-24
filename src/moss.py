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
    print (metadata_headers)
    config_name, metadata_dict, input, sample_name, entry_id, target_dir, ref_db, c_name = moss.moss_init(config_name, metadata, metadata_headers)
    moss.sql_execute_command("INSERT INTO sample_table(entry_id, sample_name, reference_id, amr_genes, virulence_genes, plasmids) VALUES('{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entry_id, sample_name, "", "", "", "", ""), config_name)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("CGE finders", sample_name, "Not Determined", "1", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\""\
                             .format("CGE finders", sample_name, "Not Determined", "2", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    moss.moss_mkfs(config_name, entry_id)

    os.system("mkdir {}/finders".format(target_dir))
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "resfinder", target_dir, input, "/opt/moss/resfinder_db/all")
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "virulencefinder", target_dir, input, "/opt/moss/virulencefinder_db/all")
    moss.kma_finders("-ont -md 5 -1t1 -cge -apm", "plasmidfinder", target_dir, input, "/opt/moss/plasmidfinder_db/all")

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("KMA Mapping", sample_name, "Not Determined", "3", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    template_score, template_search_result, reference_header_text, template_number = moss.kma_mapping(target_dir, input, config_name)

    associated_species = "{} - assembly from ID: {}".format(reference_header_text, entry_id)

    moss.run_mlst(input, target_dir, reference_header_text)

    resfinder_hits, virulence_hits, plasmid_hits, mlst_type = moss.push_finders_data_sql(target_dir, config_name, entry_id)

    if template_search_result == 1: #1 means error, thus no template found
        moss.run_assembly(entry_id, config_name, sample_name, target_dir, input, reference_header_text,
                          associated_species, resfinder_hits, virulence_hits, plasmid_hits, mlst_type)
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("IPC check", sample_name, "Alignment", "4", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    result, action = moss.acquire_semaphore("ipc_index_refdb", config_name, 1, 7200)
    if result == 'acquired' and action == False:
        moss.release_semaphore("ipc_index_refdb", config_name)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured. ipc_index_refdb update')

    if " " in reference_header_text:
        templateaccesion = reference_header_text.split(" ")[0]
    else:
        templateaccesion = reference_header_text

    consensus_name = "{}_{}_consensus".format(c_name, templateaccesion) #TBD fix consensus name

    moss.nanopore_alignment(input, template_number, target_dir, consensus_name, config_name)

    reference_id = moss.sql_fetch("SELECT entry_id FROM reference_table WHERE reference_header_text = '{}'".format(reference_header_text), config_name)[0][0]

    moss.sql_execute_command("UPDATE sample_table SET reference_id = '{}' WHERE entry_id = '{}'".format(reference_id, entry_id), config_name)

    cmd = "cp {}{}.fsa /opt/moss_db/{}/consensus_sequences/{}.fsa".format(target_dir, consensus_name, config_name, consensus_name)
    os.system(cmd)

    moss.sql_execute_command("UPDATE sample_table SET consensus_name = '{}.fsa' WHERE entry_id = '{}'".format(consensus_name, entry_id), config_name)

    related_isolates = moss.sql_fetch("SELECT consensus_name FROM sample_table WHERE reference_id = '{}'".format(reference_id), config_name)[0][0].split(",")

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("CCphylo", sample_name, "Alignment", "5", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    moss.make_phytree_output_folder(config_name, target_dir, related_isolates, reference_header_text)

    cmd = "/opt/moss/ccphylo/ccphylo dist --input {}/phytree_output/* --reference \"{}\" --min_cov 0.01 --normalization_weight 0 --output {}/phytree_output/distance_matrix".format(target_dir, reference_header_text, target_dir)
    os.system(cmd)

    distance = moss.ThreshholdDistanceCheck("{}/phytree_output/distance_matrix".format(target_dir), reference_header_text.split()[0]+".fsa", consensus_name+".fsa")

    if distance > 300: #SNP distance
        associated_species = "{} - assembly from ID: {}".format(reference_header_text, entry_id)
        moss.run_assembly(entry_id, config_name, sample_name, target_dir, input, reference_header_text,
                          associated_species, resfinder_hits, virulence_hits, plasmid_hits, mlst_type)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Distance Matrix", sample_name, "Alignment", "6", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    cmd = "/opt/moss/ccphylo/ccphylo tree --input {}/phytree_output/distance_matrix --output {}/phytree_output/tree.newick".format(target_dir, target_dir)
    os.system(cmd)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Phylo Tree imaging", sample_name, "Alignment", "7", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    image_location = moss.create_phylo_tree(target_dir)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Database updating", sample_name, "Alignment", "8", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF", sample_name, "Alignment", "9", "10", "Running", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)


    moss.compileReportAlignment(target_dir, entry_id, config_name, reference_header_text, related_isolates, resfinder_hits, virulence_hits, plasmid_hits, mlst_type, sample_name) #No report compiled for assemblies! Look into it! #TBD

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Completed", sample_name, "Alignment", "10", "10", "Completed", str(datetime.datetime.now())[0:-7], entry_id)
    moss.sql_execute_command(sql_cmd, config_name)

def main():
    moss_pipeline(args.config_name, args.metadata, args.metadata_headers)


if __name__== "__main__":
  main()
