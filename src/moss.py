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
import mbh_helpers as mbh_helper
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

    db_dir, exepath, metadata_dict, input, inputType, total_filenames, assemblyType, samplename, entryid, illumina_name1, illumina_name2 = moss.moss_init(seqType, prune_distance, bc,
                         db_dir, multi_threading, exepath, laptop, metadata, metadata_headers)

    #Init_func to check practicalities, create directories etc. Use linux built-in func

    #MAKE function for mkfs TBD

    #Remove the sql function belove for one, query based function

    moss.sql_execute_command("INSERT INTO isolatetable(entryid, header_text, samplename, analysistimestamp, plasmids, amrgenes, virulencegenes, referenceid) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
        entryid, "Initializing", samplename, str(datetime.datetime.now())[0:-7], plasmid_string.replace("'", "''"),
        allresgenes.replace(", ", ",").replace("'", "''"), virulence_string.replace("'", "''"), referenceid), db_dir)

    moss.sql_execute_command("INSERT INTO statustable(entryid, status, type, current_stage, final_stage, result) VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(
        entryid, "Initializing", samplename, "1", "10", "Running", db_dir, ''), db_dir)

    #Managed below in the init function
    kma_database_path, logfile = moss.moss_mkfs(db_dir, entryid) #TBD


    #Make mbh_helper pip lib for practice and future work. Dont use print, but use linux concat to not have to open file the entirety.
    mbh_helper.print_to_logfile("# input: {}".format(total_filenames), logfile, True)

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CGE_finders", "Not Determined", "2", "10", "Running", db_dir), db_dir)

    mbh_helper.print_to_logfile("# Running CGE tool: {}".format("Resfinder"), logfile, True)

    #Rewrite finders with alfred's CGElib
    moss.runResFinder(exepath, total_filenames, target_dir, seqType)
    mbh_helper.print_to_logfile("# Running CGE tool: {}".format("PlasmidFinder"), logfile, True)
    moss.runPlasmidFinder(exepath, total_filenames, target_dir)
    mbh_helper.print_to_logfile("# Running CGE tool: {}".format("VirulenceFinder"), logfile, True)
    moss.runVirulenceFinder(exepath, total_filenames, target_dir)
    mbh_helper.print_to_logfile("# Running KMA mapping for template identification", logfile, True)

    #Rewrite this horrible kma_mapping function. Should be way simpler.
    best_template_score, template_found, header_text = moss.KMA_mapping(total_filenames, target_dir, kma_database_path, logfile, exepath + "kma/kma", laptop)

    #Rewrite MLST finder perhaps
    mlst_result = moss.run_mlst(exepath, total_filenames, target_dir, header_text, seqType)

    #Genertic SQL query
    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "KMA Mapping", "Not Determined", "3", "10", "Running", db_dir), db_dir)

    #This should be done during kma mapping!
    best_template = moss.findTemplateNumber(db_dir, header_text)

    mbh_helper.print_to_logfile("Best template number: {}".format(best_template), logfile, True)

    #Like what the actual F is this. Instead, during new CGE finders, make sure output in sql compatiable.
    #Also, we dont need random data now. Should be fetched seperately and used independently.
    plasmid_count, plasmid_list = moss.plasmid_data_for_report(target_dir + "plasmidFinderResults/data.json",
                                                               target_dir)
    plasmid_string = ",".join(plasmid_list)
    virulence_count, virulence_list = moss.virulence_data_for_report(target_dir + "virulenceFinderResults/data.json",
                                                                     target_dir, logfile)
    virulence_string = ",".join(virulence_list)

    #Scrap warning? TBD program should be leaner with fewer, completed functions SCRAP
    warning, riskcategory, allresgenes, amrinfo = moss.checkAMRrisks(target_dir, entryid, db_dir, header_text, exepath,
                                                                     logfile)

    moss.sql_execute_command("UPDATE isolatetable SET {}, {}, {}, {}, {} WHERE {}".format(entryid, header_text, samplename,
                                                    plasmid_string.replace("'", "''"),
                                                    allresgenes.replace(", ", ",").replace("'", "''"),
                                                    virulence_string.replace("'", "''"), db_dir))

    #New section
    if best_template == None:
        template_found = False

    mbh_helper.print_to_logfile("Best template: {}".format(header_text), logfile, True)

    mbh_helper.print_to_logfile("Best template score: " + str(best_template_score), logfile, True)

    if template_found == False: #NO TEMPLATE FOUND #Being assembly
        #SCRAP associated species, wtf it is even used for
        associated_species = "No related reference identified, manual curation required. ID: {} name: {}".format(
            entryid, samplename)
        moss.run_assembly(entryid, db_dir, samplename, assemblyType, inputType, target_dir, input, illumina_name1,
                          illumina_name2, jobid, exepath, kma_database_path, start_time, logfile, associated_species)

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "IPC check", "Alignment", "4", "10", "Running", db_dir), db_dir)

    #Semaphores should be managed better tbh. Function within function?
    result, action = moss.acquire_semaphore("ipc_index_refdb", db_dir, 1, 7200)
    if result == 'acquired' and action == False:
        moss.release_semaphore("ipc_index_refdb", db_dir)
    elif result != 'acquired' and action == True:
        result += " : ipc_index_refdb"
        sys.exit(result)
    else:
        sys.exit('A semaphore related issue has occured. ipc_index_refdb update')

    #Dont manage SQL compatibility in mainscript. def variables earlier or in functions and return.
    if " " in header_text:
        templateaccesion = header_text.split(" ")[0]
    else:
        templateaccesion = header_text

    #WTF here, managed  variablenames earlier, in functions or not at all!
    if input[0].split("/")[-1][-2:] == "gz":
        c_name = input[0].split("/")[-1][:-2]
    else:
        c_name = input[0].split("/")[-1][:10]

    #Again, see above
    consensus_name = "{}_{}_consensus".format(c_name, templateaccesion)

    #actually ok, but no difference between seqType variable names.
    if inputType == "pe_illumina":
        moss.illuminaMappingPE(input, best_template, target_dir, kma_database_path, logfile, multi_threading, exepath + "kma/kma", templateaccesion, db_dir, laptop, consensus_name)
    elif inputType == "se_illumina":
        moss.illuminaMappingForward(input, best_template, target_dir, kma_database_path, logfile, multi_threading, exepath + "kma/kma", templateaccesion, db_dir, laptop, consensus_name)
    if inputType == "nanopore":
        moss.nanoporeMapping(input, best_template, target_dir, kma_database_path, logfile, multi_threading, bc, exepath + "kma/kma", templateaccesion, db_dir, laptop, consensus_name)

    referenceid = moss.sql_fetch("SELECT entryid FROM referencetable WHERE header_text = '{}'".format(header_text), db_dir)[0][0]

    moss.sql_execute_command("UPDATE isolatetable SET referenceid = '{}' WHERE entryid = '{}'".format(referenceid, entryid), db_dir)

    #Managed in function when consensus in created ffs.
    cmd = "cp {}{}.fsa {}/consensus_sequences/{}.fsa".format(target_dir, consensus_name, db_dir, consensus_name)
    os.system(cmd)

    #Generic SQL query
    moss.sql_execute_command("UPDATE isolatetable SET consensus_name = '{}.fsa' WHERE entryid = '{}'".format(consensus_name, entryid), db_dir)
    related_isolates = moss.sql_fetch("SELECT consensus_name FROM isolatetable WHERE referenceid = '{}'".format(referenceid), db_dir)[0][0].split(",")

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "CCphylo", "Alignment", "5", "10", "Running", db_dir), db_dir)


    #Fine, but can we include add ccphylo related in one function?
    moss.make_phytree_output_folder(db_dir, target_dir, related_isolates, exepath, header_text)

    #Why is cc phylo not in a function?
    cmd = "{} dist -i {}/phytree_output/* -r \"{}\" -mc 0.01 -nm 0 -o {}/phytree_output/distance_matrix".format(exepath + "ccphylo/ccphylo", target_dir, header_text, target_dir)
    print (cmd, file = logfile)

    if prune_distance != 0 :
        cmd += " -pr {}".format(prune_distance)
    os.system(cmd)


    # Check if acceptable snp distance
    distance = moss.ThreshholdDistanceCheck("{}/phytree_output/distance_matrix".format(target_dir), header_text.split()[0]+".fsa", consensus_name+".fsa")
    #Print in function ffs
    print ("Distance : " + str(distance), file = logfile)
    print ("Distance : " + str(distance))

    if distance > 300: #SNP distance
        #No associated species
        header_text = header_text.split()
        associated_species = "{} {} assembly from ID: {}, SNP distance from best verified reference: {}".format(header_text[1], header_text[2], entryid, distance)
        moss.run_assembly(entryid, db_dir, samplename, assemblyType, inputType, target_dir, input, illumina_name1,
                          illumina_name2, jobid, exepath, kma_database_path, start_time, logfile, associated_species)
    #generic sql query
    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Distance Matrix", "Alignment", "6", "10", "Running", db_dir), db_dir)

    #ccphylo in function
    cmd = "{}ccphylo/ccphylo tree -i {}/phytree_output/distance_matrix -o {}/phytree_output/tree.newick".format(exepath, target_dir, target_dir)
    os.system(cmd)

    #Include all of the below in alignment_related_function
    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Phylo Tree imaging", "Alignment", "7", "10", "Running", db_dir), db_dir)


    image_location = moss.create_phylo_tree(db_dir, header_text, target_dir)

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Database updating", "Alignment", "8", "10", "Running", db_dir), db_dir)

    #moss_sql.update_reference_table(entryid, None, None, None, header_text, db_dir)

    moss.sql_execute_command("INSERT INTO amrtable(entryid, samplename, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(entryid, samplename, str(datetime.datetime.now())[0:-7], allresgenes.replace("'", "''"), amrinfo.replace("'", "''"), header_text, riskcategory.replace("'", "''"), warning.replace("'", "''")), db_dir)

    moss.sql_execute_command("UPDATE isolatetable SET {}, {}, {}, {}, {} WHERE {}".format(entryid, header_text, samplename, plasmid_string.replace("'", "''"), allresgenes.replace(", ", ",").replace("'", "''"), virulence_string.replace("'", "''")), db_dir)

    entries, values = moss.sql_string_metadata(metadata_dict)

    moss.sql_execute_command("INSERT INTO metadatatable(entryid, {}) VALUES('{}', {})".format(entries, entryid.replace("'", "''"), values), db_dir)

    new_plasmid_string, new_virulence_string, new_amr_string = moss.scan_reference_vs_isolate_cge(plasmid_string, allresgenes.replace(", ", ","), virulence_string, header_text, db_dir)

    #Get ride of these strings. Make relational tables for genes too.

    moss.update_reference_table(entryid, new_amr_string, new_virulence_string, new_plasmid_string, header_text, db_dir)

    end_time = datetime.datetime.now()
    run_time = end_time - start_time
    print("Run time: {}".format(run_time))
    print("Run time: {}".format(run_time), file=logfile)

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Outbreak Finder", "Alignment", "9", "10", "Running", db_dir), db_dir)

    #Outbreak_finder wtf? really?
    cmd = "python3 {}src/outbreak_finder.py -db_dir {}".format(exepath, db_dir) #WTF TBD
    os.system(cmd)

    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Running", db_dir), db_dir)

    #Still fails here for multiple non-sync analyses
    #Both alignment report and assembly is fuckly. Fix it.
    moss.compileReportAlignment(target_dir, entryid, db_dir, image_location, header_text, exepath, related_isolates) #No report compiled for assemblies! Look into it! #TBD

    logfile.close()
    moss.sql_execute_command("UPDATE statustable SET {}, {}, {}, {}, {}, {} WHERE {}".format(entryid, "Alignment PDF compiling", "Alignment", "10", "10", "Finished", db_dir), db_dir)


def main():
    moss_pipeline(args.configname, args.metadata, args.metadata_headers)


if __name__== "__main__":
  main()
