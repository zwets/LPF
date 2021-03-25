#!/usr/bin/env python3

# Copyright (c) 2018, Malte Bjørn Hallgren Technical University of Denmark
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
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3


#Use Argparse to correctly open the inputfiles

parser = argparse.ArgumentParser(prog='MinION-Typer-2.0')
parser.add_argument('-info', action='store_true', help='MinION-Typer info:')
subparsers = parser.add_subparsers(help='sub-command help')
# create the parser for the "surveillance" command


parser_surveillance = subparsers.add_parser('surveillance', help='surveillance help')
parser_surveillance.add_argument('-info', type=int, help='surveillance info')
parser_surveillance.add_argument('-i_illumina', nargs='+', action="store", type=str, dest='i_illumina', default="", help='Use this function is you only have a single illumina entry. Otherwise, if you have multiple, use i_path_illumina.')
parser_surveillance.add_argument('-i_nanopore', action="store", type=str, dest='i_nanopore', default="", help='Use this function is you only have a single nanopore entry. Otherwise, if you have multiple, use nanopore.')
parser_surveillance.add_argument("-pe", action="store_true", dest="paired_end", default = False, help="If paipred ends are used give input as True (-pe True). If Paired-ends are used, it is important that the files are written in the correct order, such as: sample1_1.fasta sample1_2.fasta sample2_1.fasta sample2_1.fasta")
parser_surveillance.add_argument("-dcmMethylation", type=str, action="store", dest="dcmMethylation", default="", help="Will mask the dcmMethylation patterns matching CC[X]GG, where X will be ")
parser_surveillance.add_argument("-prune", action="store_true", dest="prune", default = False, help="If set to true, all SNPs that are located within 10 bp will not be included")
parser_surveillance.add_argument("-prune_distance", type=int, action="store", dest="prune_distance", default=10, help="X lenght that SNPs can be located between each other. Default is 10. If two SNPs are located within X lenght of eachother, everything between them as well as X lenght on each side of the SNPs will not be used in the alignments to calculate the distance matrix.")
parser_surveillance.add_argument("-bc", action="store", type=float, default = 0.7, dest="bc", help="Base calling parameter for nanopore KMA mapping. Default is 0.7")
parser_surveillance.add_argument("-ref_kma_db", action="store", type=str, default = "", dest="ref_kma_database", help="Comeplete path for the ref_kma_database for KMA mapping")
parser_surveillance.add_argument("-isolate_db", action="store", type=str, default = "", dest="isolate_database", help="Comeplete path for the isolate database created with MinION-Typer_initializer.py")
parser_surveillance.add_argument("-isolate_storage", action="store", type=str, default = "", dest="isolate_storage", help="")
parser_surveillance.add_argument("-reference_storage", action="store", type=str, default = "", dest="reference_storage", help="")
parser_surveillance.add_argument("-thread", action="store", default = 1, dest="multi_threading", help="Set this parameter to x-number of threads that you would like to use during KMA-mapping.")
#parser_surveillance.add_argument("-ref", action="store", type=str, default = "", dest="reference", help="KMA will by default determine the best template against the given database. However, if you want to align your query sequences against a reference of your own choice, use this function. If this is left blank, KMA will determine the optimal reference.")
parser_surveillance.add_argument("-o", action="store", dest="output_name", help="Name that you would like the output directory to be called.")
parser_surveillance.add_argument('-version', action='version', version='MinION-Typer 1.0.0', help = "current version of MinION-Typer")
parser_surveillance.add_argument("-o_path", action="store", type=str, default="", dest="output_path", help="If you would like your output directory to be located in a specific place, use this function. If this function is not used, the output folder will be placed in the working directory. Remember your stated output_directory must end on a dash! Also, remember that this is only the path to the output directory, so the name of your output directory must also be stated using the -o function. An example of correct use of this would be : -o_path /home/user/myDirectory/ -o myNewDirectory ")

# create the parser for the "research" command
parser_research = subparsers.add_parser('research', help='research help')
parser_research.add_argument('-info', type=int, help='research info')
parser_research.add_argument('-i_path_illumina', action="store", type=str, dest='i_path_illumina', default="", help='The path to the directory containing ONLY the input illumina files. Should be used when analyzing >5 read-files at a time.')
parser_research.add_argument('-i_path_nanopore', action="store", type=str, dest='i_path_nanopore', default="", help='The path to the directory containing ONLY the input nanopore files. Should be used when analyzing >5 read-files at a time.')
parser_research.add_argument("-pe", action="store_true", dest="paired_end", default = False, help="If paipred ends are used give input as True (-pe True). If Paired-ends are used, it is important that the files are written in the correct order, such as: sample1_1.fasta sample1_2.fasta sample2_1.fasta sample2_1.fasta")
parser_research.add_argument("-dcmMethylation", type=str, action="store", dest="dcmMethylation", default="", help="Will mask the dcmMethylation patterns matching CC[X]GG, where X will be ")
parser_research.add_argument("-prune", action="store_true", dest="prune", default = False, help="If set to true, all SNPs that are located within 10 bp will not be included")
parser_research.add_argument("-prune_distance", type=int, action="store", dest="prune_distance", default=10, help="X lenght that SNPs can be located between each other. Default is 10. If two SNPs are located within X lenght of eachother, everything between them as well as X lenght on each side of the SNPs will not be used in the alignments to calculate the distance matrix.")
parser_research.add_argument("-bc", action="store", type=float, default = 0.7, dest="bc", help="Base calling parameter for nanopore KMA mapping. Default is 0.7")
parser_research.add_argument("-db", action="store", type=str, default = "", dest="ref_kma_database", help="Comeplete path for the ref_kma_database for KMA mapping")
parser_research.add_argument("-thread", action="store", default = 1, dest="multi_threading", help="Set this parameter to x-number of threads that you would like to use during KMA-mapping.")
parser_research.add_argument("-ref", action="store", type=str, default = "", dest="reference", help="KMA will by default determine the best template against the given database. However, if you want to align your query sequences against a reference of your own choice, use this function. If this is left blank, KMA will determine the optimal reference.")
parser_research.add_argument("-o_path", action="store", type=str, default="", dest="output_path", help="If you would like your output directory to be located in a specific place, use this function. If this function is not used, the output folder will be placed in the working directory. Remember your stated output_directory must end on a dash! Also, remember that this is only the path to the output directory, so the name of your output directory must also be stated using the -o function. An example of correct use of this would be : -o_path /home/user/myDirectory/ -o myNewDirectory ")
parser_research.add_argument('-version', action='version', version='MinION-Typer 1.0.0', help = "current version of MinION-Typer")
parser_research.add_argument("-o", action="store", dest="output_name", help="Name that you would like the output directory to be called.")

# create the parser for the "append" command
parser_append = subparsers.add_parser('append', help='append help')
parser_append.add_argument('-info', type=int, help='append info')

parser_append.add_argument('-i_path_illumina', action="store", type=str, dest='i_path_illumina', default="", help='The path to the directory containing ONLY the input illumina files. Should be used when analyzing >5 read-files at a time.')
parser_append.add_argument('-i_path_nanopore', action="store", type=str, dest='i_path_nanopore', default="", help='The path to the directory containing ONLY the input nanopore files. Should be used when analyzing >5 read-files at a time.')
parser_append.add_argument("-pe", action="store_true", dest="paired_end", default = False, help="If paipred ends are used give input as True (-pe True). If Paired-ends are used, it is important that the files are written in the correct order, such as: sample1_1.fasta sample1_2.fasta sample2_1.fasta sample2_1.fasta")
parser_append.add_argument("-o_path", action="store", type=str, default="", dest="output_path", help="If you would like your output directory to be located in a specific place, use this function. If this function is not used, the output folder will be placed in the working directory. Remember your stated output_directory must end on a dash! Also, remember that this is only the path to the output directory, so the name of your output directory must also be stated using the -o function. An example of correct use of this would be : -o_path /home/user/myDirectory/ -o myNewDirectory ")
parser_append.add_argument("-o", action="store", dest="output_name", help="Name that you would like the output directory to be called.")

#parser.add_argument('-i_path_illumina', action="store", type=str, dest='i_path_illumina', default="", help='The path to the directory containing ONLY the input illumina files. Should be used when analyzing >5 read-files at a time.')
#parser.add_argument('-i_path_nanopore', action="store", type=str, dest='i_path_nanopore', default="", help='The path to the directory containing ONLY the input nanopore files. Should be used when analyzing >5 read-files at a time.')
#parser.add_argument("-pe", action="store_true", dest="paired_end", default = False, help="If paipred ends are used give input as True (-pe True). If Paired-ends are used, it is important that the files are written in the correct order, such as: sample1_1.fasta sample1_2.fasta sample2_1.fasta sample2_1.fasta")
#parser.add_argument("-dcmMethylation", type=str, action="store", dest="dcmMethylation", default="", help="Will mask the dcmMethylation patterns matching CC[X]GG, where X will be ")
#parser.add_argument("-prune", action="store_true", dest="prune", default = False, help="If set to true, all SNPs that are located within 10 bp will not be included")
#parser.add_argument("-prune_distance", type=int, action="store", dest="prune_distance", default=10, help="X lenght that SNPs can be located between each other. Default is 10. If two SNPs are located within X lenght of eachother, everything between them as well as X lenght on each side of the SNPs will not be used in the alignments to calculate the distance matrix.")
#parser.add_argument("-bc", action="store", type=float, default = 0.7, dest="bc", help="Base calling parameter for nanopore KMA mapping. Default is 0.7")
#parser.add_argument("-db", action="store", type=str, default = "", dest="ref_kma_database", help="Comeplete path for the ref_kma_database for KMA mapping")
#parser.add_argument("-thread", action="store", default = 1, dest="multi_threading", help="Set this parameter to x-number of threads that you would like to use during KMA-mapping.")
#parser.add_argument("-ref", action="store", type=str, default = "", dest="reference", help="KMA will by default determine the best template against the given database. However, if you want to align your query sequences against a reference of your own choice, use this function. If this is left blank, KMA will determine the optimal reference.")
#parser.add_argument("-appendPipeline", action="store_true", default = False, dest="appendPipeline", help="appendPipeline")
#parser.add_argument("-appendPipelineLogFile", action="store", type=str, default = "", dest="appendPipelineLogFile", help="appendPipelineFile")
#parser.add_argument("-researchPipeline", action="store_true", default = False, dest="researchPipeline", help="researchPipeline")
#parser.add_argument("-o_path", action="store", type=str, default="", dest="output_path", help="If you would like your output directory to be located in a specific place, use this function. If this function is not used, the output folder will be placed in the working directory. Remember your stated output_directory must end on a dash! Also, remember that this is only the path to the output directory, so the name of your output directory must also be stated using the -o function. An example of correct use of this would be : -o_path /home/user/myDirectory/ -o myNewDirectory ")
#parser.add_argument('-version', action='version', version='MinION-Typer 1.0.0', help = "current version of MinION-Typer")
#parser.add_argument("-o", action="store", dest="output_name", help="Name that you would like the output directory to be called.")
args = parser.parse_args()

def find_best_template(total_filenames, target_dir, kma_database_path, logfile, surveillanceRun, researchRun, appendRun):
    no_template_found = False
    best_template = ""
    best_template_score = 0.0
    templatename = ""
    if surveillanceRun == False:
        reference = args.reference
    else:
        reference = ""
    if reference != "":
        best_template = reference
        print("# The reference given by the user was: " + best_template, file=logfile)
        print("#Making articial DB", file=logfile)
        cmd = "kma_index -i " + best_template + " -o " + target_dir + "temdb.ATG -Sparse ATG"
        os.system(cmd)
        print("# Mapping reads to template", file=logfile)
        cmd = "kma -i " + total_filenames + " -o " + target_dir + "template_kma_results" + " -t_db " + target_dir + "temdb.ATG" + " -Sparse -mp 20"
        os.system(cmd)
        try:
            infile_template = open(target_dir + "template_kma_results.spa", 'r')
            line = infile_template.readlines()[1]
            best_template = line.split("\t")[1]
            templatename = line.split("\t")[0]
            infile_template.close()
        except IndexError as error:
            print ("The template you have stated as a reference does not match the input reads to a good enough degree to make any type of analysis.")
            sys.exit()
        print("# Best template found was " + templatename, file=logfile)
        print("#Template number was: " + str(best_template), file=logfile)
        cmd = "kma seq2fasta -t_db " + target_dir + "temdb -seqs " + str(best_template) + " > " + target_dir + "template_sequence"
        os.system(cmd)
        print("# Mapping reads to template", file=logfile)
        return best_template
    else:
        print("# Finding best template", file=logfile)
        cmd = "kma -i " + total_filenames + " -o " + target_dir + "template_kma_results" + " -ID 50 -t_db " + kma_database_path + " -Sparse -mp 20"
        print ("DID KMA NO SPARSE TEST")
        os.system(cmd)
        "Tried finding best template"
        try:
            infile_template = open(target_dir + "template_kma_results.spa", 'r')
            line = infile_template.readlines()[1]
            best_template = line.split("\t")[1]
            templatename = line.split("\t")[0]
            #scoring of matches, loop through and fine all maatches of 97%> BTD
            best_template_score = float(line.split("\t")[6])
            if best_template_score < 90.00:
                print (
                    "None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.")
                print (
                "None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.",
                file=logfile)
                # Perform assembly based on input
                no_template_found = True
                return best_template, best_template_score, no_template_found, templatename
            infile_template.close()
        except IndexError as error:
            print ("None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.")
            print ("None of the given templates matches any of the entries in given ref_kma_database. The input reads will now be assembled and added to the reference ref_kma_database as a new reference. After this the program will be stopped, and thus no distance matrix based analysis will be carried out.", file=logfile)
            #Perform assembly based on input
            if surveillanceRun == True:
                print ("found surveillance")
                #Assemble
                #Append as reference to both DB's
                #End with message
            elif researchRun == True:
                print ("found research")
            elif appendRun == True:
                print ("found append")
            no_template_found = True
            return best_template, best_template_score, no_template_found, templatename
        print("# Best template found was " + templatename, file=logfile)
        print("# Template number was: " + str(best_template), file=logfile)
        cmd = "kma seq2fasta -t_db " + kma_database_path + " -seqs " + str(best_template) + " > " + target_dir + "template_sequence"
        os.system(cmd)
        print("# Mapping reads to template", file=logfile)
        return best_template, best_template_score, no_template_found, templatename


#Mapping
def mapping_illumina(complete_path_illumina_input, illumina_input, paired_end, best_template, target_dir, kma_database_path, logfile, multi_threading, surveillanceRun):
    if surveillanceRun == False:
        reference = args.reference
    else:
        reference = ""

    if reference != "":
        kma_database_path = target_dir + "temdb"
    # Illumina input
    if illumina_input != "" and paired_end == False:
        for i in range(len(illumina_input)):
            cmd = "kma -i " + complete_path_illumina_input[i] + " -o " + target_dir + illumina_input[i] + "_mapping_results"  + " -t_db " + kma_database_path + " -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 " + str(best_template) + " -t " + str(multi_threading)
            os.system(cmd)
    elif illumina_input != "" and paired_end == True:
        for i in range(0, len(illumina_input), 2):
            cmd = "kma -ipe " + complete_path_illumina_input[i] + " " + complete_path_illumina_input[i + 1] + " -o " + target_dir + illumina_input[i] + "_mapping_results" + " -t_db " + kma_database_path + " -ref_fsa -ca -dense -cge -vcf -bc90 -Mt1 " + str(best_template) + " -t " + str(multi_threading)
            os.system(cmd)
    print ("# Illumina mapping completed succesfully", file=logfile)
def mapping_nanopore(complete_path_nanopore_input, nanopore_input, best_template, target_dir, kma_database_path, logfile, multi_threading, surveillanceRun):
    # Nanopore input

    if surveillanceRun == False:
        reference = args.reference
    else:
        reference = ""

    if reference != "":
        kma_database_path = target_dir + "temdb"
    if nanopore_input != "":
        for i in range(0, len(nanopore_input)):
            cmd = "kma -i " + complete_path_nanopore_input[i] + " -o " + target_dir + nanopore_input[i] + "_mapping_results" + " -t_db " + kma_database_path + " -mp 20 -1t1 -dense -vcf -ref_fsa -ca -bcNano -Mt1 " + str(best_template) + " -t " + str(multi_threading) + " -bc " + str(args.bc)
            os.system(cmd)
    print ("# Nanopore mapping completed succesfully", file=logfile)


def dcmMethylationFunction(dcmMethylation, nanopore_input, illumina_input, target_dir, logfile, dcmfilename):
    dcmfile = open(dcmfilename, 'w')

    if dcmMethylation == "":
        dcmMethylationBases = "ATGC"
    elif dcmMethylation.upper() == "A" or dcmMethylation.upper() == "C" or dcmMethylation.upper() == "G" or dcmMethylation.upper() == "T":
        dcmMethylationBases = dcmMethylation.upper()
    elif dcmMethylation.upper() == "R":
        dcmMethylationBases = "AG"
    elif dcmMethylation.upper() == "Y":
        dcmMethylationBases = "CT"
    elif dcmMethylation.upper() == "M":
        dcmMethylationBases = "AC"
    elif dcmMethylation.upper() == "K":
        dcmMethylationBases = "GT"
    elif dcmMethylation.upper() == "S":
        dcmMethylationBases = "CG"
    elif dcmMethylation.upper() == "W":
        dcmMethylationBases = "AT"
    elif dcmMethylation.upper() == "H":
        dcmMethylationBases = "ACT"
    elif dcmMethylation.upper() == "B":
        dcmMethylationBases = "CGT"
    elif dcmMethylation.upper() == "V":
        dcmMethylationBases = "ACG"
    elif dcmMethylation.upper() == "D":
        dcmMethylationBases = "AGT"
    elif dcmMethylation.upper() == "N":
        dcmMethylationBases = "ATGC"


    templateseqfile = open(target_dir + "template_sequence", 'r')
    sequence = ""
    for line in templateseqfile:
        if line[0] != ">":
            line = line.rstrip()
            sequence += line
    startFrame = "CC"
    endFrame = "GG"
    motifNumber = len(dcmMethylationBases)
    possibleFrames = []
    for i in range(motifNumber):
        frame = startFrame + dcmMethylationBases[i] + endFrame
        possibleFrames.append(frame)
    motif_positions = []
    motifcount = 0
    for i in range(len(sequence)-5):
        if sequence[i:i+5] in possibleFrames:
            motif_positions.append(i)
            motifcount += 1
    print (str(motifcount) + " occurrences of dcmMethylation motifs found in the template, but they have NOT yet been masked", file = logfile)
    print (">start" + "\t" + "end", file = dcmfile)
    for i in range(len(motif_positions)):
        print (str(motif_positions[i]) + "\t" + str(motif_positions[i]+5), file = dcmfile)
    if dcmMethylation != "":
        print (str(motifcount) + " occurrences of dcmMethylation motifs found in the template has been masked!", file = logfile)
            #removing dcm-positions in mapped reads
        if nanopore_input != "":
                for i in range(len(nanopore_input)):
                    openname = target_dir + nanopore_input[i] + "_mapping_results.fsa"
                    openfile = open(openname, 'r')
                    writename = target_dir + nanopore_input[i] + "_mapping_results.fsa" + "write"
                    writefile = open(writename, 'w')
                    sequence = ""
                    for line in openfile:
                        if line[0] != '>':
                            line = line.rstrip()
                            sequence += line
                        else:
                            line = line.rstrip()
                            header = line
                            print (header, file = writefile)
                    for i in range(len(motif_positions)):
                        sequence = sequence[:int(motif_positions[i])] + "NNNNN" + sequence[int(motif_positions[i]) + 5:]
                    for i in range(len(sequence)-5):
                        if sequence[i:i+5] in possibleFrames:
                            sequence = sequence[:i] + "NNNNN" + sequence[i+5:]
                    print (sequence, file = writefile)
                    openfile.close()
                    writefile.close()
                    cmd = "rm " + openname
                    os.system(cmd)
                    cmd = "mv " + writename + " " + openname
                    os.system(cmd)
        if illumina_input != "":
            if args.paired_end == False:
                for i in range(len(illumina_input)):
                    openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
                    openfile = open(openname, 'r')
                    writename = target_dir + illumina_input[i] + "_mapping_results.fsa" + "write"
                    writefile = open(writename, 'w')
                    sequence = ""
                    for line in openfile:
                        if line[0] != '>':
                            line = line.rstrip()
                            sequence += line
                        else:
                            line = line.rstrip()
                            header = line
                            print (header, file = writefile)
                    for i in range(len(motif_positions)):
                        sequence = sequence[:int(motif_positions[i])] + "NNNNN" + sequence[int(motif_positions[i]) + 5:]
                    for i in range(len(sequence)-5):
                        if sequence[i:i+5] in possibleFrames:
                            sequence = sequence[:i] + "NNNNN" + sequence[i+5:]
                    print (sequence, file = writefile)
                    openfile.close()
                    writefile.close()
                    cmd = "rm " + openname
                    os.system(cmd)
                    cmd = "mv " + writename + " " + openname
                    os.system(cmd)
            if args.paired_end == True:
                for i in range(0, len(illumina_input), 2):
                    openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
                    openfile = open(openname, 'r')
                    writename = target_dir + illumina_input[i] + "_mapping_results.fsa" + "write"
                    writefile = open(writename, 'w')
                    sequence = ""
                    for line in openfile:
                        if line[0] != '>':
                            line = line.rstrip()
                            sequence += line
                        else:
                            line = line.rstrip()
                            header = line
                            print (header, file = writefile)
                    for i in range(len(motif_positions)):
                        sequence = sequence[:int(motif_positions[i])] + "NNNNN" + sequence[int(motif_positions[i]) + 5:]
                    for i in range(len(sequence)-5):
                        if sequence[i:i+5] in possibleFrames:
                            sequence = sequence[:i] + "NNNNN" + sequence[i+5:]
                    print (sequence, file = writefile)
                    openfile.close()
                    writefile.close()
                    cmd = "rm " + openname
                    os.system(cmd)
                    cmd = "mv " + writename + " " + openname
                    os.system(cmd)
    dcmfile.close()

def prune_nanopore(prune, nanopore_input, target_dir, prune_distance):
    if prune == True and nanopore_input != "":
        for i in range(len(nanopore_input)):
            openname = target_dir + nanopore_input[i] + "_mapping_results.aln"
            template = []
            templatefile = open(openname, 'r')
            for line in templatefile:
                if line[0:8] == 'template':
                    line = line.rstrip()
                    line = line.split('\t')
                    for t in range(len(line[1])):
                        template.append(line[1][t])
            openname = target_dir + nanopore_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            query = []
            for line in readfile:
                if line[0] != '>':
                    line = line.rstrip()
                    for i in range(len(line)):
                        query.append(line[i])
                else:
                    line = line.rstrip()
                    header = line
            # locate snps
            bad_snps = []
            snp_list = []
            for i in range(len(template)):
                if query[i].upper() != 'N' and query[i].upper() != template[i]:
                    snp_list.append(i)
            # remove too close snp areas
            for i in range(len(snp_list) - 1):
                if prune_distance >= (snp_list[i + 1] - snp_list[i]):
                    bad_snps.append(snp_list[i])
                    bad_snps.append(snp_list[i + 1])
            cleaned_bad_snips = []
            bad_snps.sort()
            if bad_snps != []:
                for i in range(len(bad_snps) - 1):
                    if bad_snps[i] != bad_snps[i + 1]:
                        cleaned_bad_snips.append(bad_snps[i])
                if bad_snps[-1] != bad_snps[-2]:
                    cleaned_bad_snips.append(bad_snps[-1])
                for i in range(len(cleaned_bad_snips)):
                    if prune_distance >= cleaned_bad_snips[i]:
                        for t in range(0 - cleaned_bad_snips[i], cleaned_bad_snips[i] + (prune_distance + 1),
                                       1):
                            query[cleaned_bad_snips[i] + t] = 'n'
                    elif cleaned_bad_snips[i] >= (len(query) - prune_distance):
                        for t in range(-prune_distance, len(query) - cleaned_bad_snips[i], 1):
                            query[cleaned_bad_snips[i] + t] = 'n'
                    else:
                        for t in range(-prune_distance, (prune_distance + 1), 1):
                            query[cleaned_bad_snips[i] + t] = 'n'
                readfile.close()
                cmd = "rm " + openname
                os.system(cmd)
                newfile = open(openname, 'w')
                print(header, file=newfile)
                sequence = ("").join(query)
                print(sequence, file=newfile)
                newfile.close()

#Remove SNPs

def prune_illumina(prune, paired_end, illumina_input, target_dir, prune_distance):
    if illumina_input != "":
        if prune == True and paired_end == False:
            for i in range(len(illumina_input)):
                openname = target_dir + illumina_input[i] + "_mapping_results.aln"
                template = []
                templatefile = open(openname, 'r')
                for line in templatefile:
                    if line[0:8] == 'template':
                        line = line.rstrip()
                        line = line.split('\t')
                        for t in range(len(line[1])):
                            template.append(line[1][t])
                openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
                readfile = open(openname, 'r')
                query = []
                for line in readfile:
                    if line[0] != '>':
                        line = line.rstrip()
                        for i in range(len(line)):
                            query.append(line[i])
                    else:
                        line = line.rstrip()
                        header = line
                # locate snps
                bad_snps = []
                snp_list = []
                for i in range(len(template)):
                    if query[i].upper() != 'N' and query[i].upper() != template[i]:
                        snp_list.append(i)
                # remove too close snp areas
                for i in range(len(snp_list) - 1):
                    if prune_distance >= (snp_list[i + 1] - snp_list[i]):
                        bad_snps.append(snp_list[i])
                        bad_snps.append(snp_list[i + 1])
                cleaned_bad_snips = []
                bad_snps.sort()
                if bad_snps != []:
                    for i in range(len(bad_snps) - 1):
                        if bad_snps[i] != bad_snps[i + 1]:
                            cleaned_bad_snips.append(bad_snps[i])
                    if bad_snps[-1] != bad_snps[-2]:
                        cleaned_bad_snips.append(bad_snps[-1])
                    for i in range(len(cleaned_bad_snips)):
                        if prune_distance >= cleaned_bad_snips[i]:
                            for t in range(0 - cleaned_bad_snips[i], cleaned_bad_snips[i] + (prune_distance + 1),
                                           1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                        elif cleaned_bad_snips[i] >= (len(query) - prune_distance):
                            for t in range(-prune_distance, len(query) - cleaned_bad_snips[i], 1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                        else:
                            for t in range(-prune_distance, (prune_distance + 1), 1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                    readfile.close()
                    cmd = "rm " + openname
                    os.system(cmd)
                    newfile = open(openname, 'w')
                    print(header, file=newfile)
                    sequence = ("").join(query)
                    print(sequence, file=newfile)
                    newfile.close()

        if prune == True and paired_end == True:
            for i in range(0, len(illumina_input), 2):
                openname = target_dir + illumina_input[i] + "_mapping_results.aln"
                template = []
                templatefile = open(openname, 'r')
                for line in templatefile:
                    if line[0:8] == 'template':
                        line = line.rstrip()
                        line = line.split('\t')
                        for t in range(len(line[1])):
                            template.append(line[1][t])
                openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
                readfile = open(openname, 'r')
                query = []
                for line in readfile:
                    if line[0] != '>':
                        line = line.rstrip()
                        for i in range(len(line)):
                            query.append(line[i])
                    else:
                        line = line.rstrip()
                        header = line
                # locate snps
                bad_snps = []
                snp_list = []
                for i in range(len(template)):
                    if query[i].upper() != 'N' and query[i].upper() != template[i]:
                        snp_list.append(i)
                # remove too close snp areas
                for i in range(len(snp_list) - 1):
                    if prune_distance >= (snp_list[i + 1] - snp_list[i]):
                        bad_snps.append(snp_list[i])
                        bad_snps.append(snp_list[i + 1])
                cleaned_bad_snips = []
                bad_snps.sort()
                if bad_snps != []:
                    for i in range(len(bad_snps) - 1):
                        if bad_snps[i] != bad_snps[i + 1]:
                            cleaned_bad_snips.append(bad_snps[i])
                    if bad_snps[-1] != bad_snps[-2]:
                        cleaned_bad_snips.append(bad_snps[-1])
                    for i in range(len(cleaned_bad_snips)):
                        if prune_distance >= cleaned_bad_snips[i]:
                            for t in range(0 - cleaned_bad_snips[i], cleaned_bad_snips[i] + (prune_distance + 1), 1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                        elif cleaned_bad_snips[i] >= (len(query) - prune_distance):
                            for t in range(-prune_distance, len(query) - cleaned_bad_snips[i], 1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                        else:
                            for t in range(-prune_distance, (prune_distance + 1), 1):
                                query[cleaned_bad_snips[i] + t] = 'n'
                    readfile.close()
                    cmd = "rm " + openname
                    os.system(cmd)
                    newfile = open(openname, 'w')
                    print(header, file=newfile)
                    sequence = ("").join(query)
                    print(sequence, file=newfile)
                    newfile.close()


def MultiFasta(illumina_input, nanopore_input, paired_end, target_dir, multiFastaCount):
    if multiFastaCount == 0:
        nctreefile = open(target_dir + "original_mappings_multi.fsa", 'w')
    else:
        nctreefile = open(target_dir + "nctree_input", 'w')
    ###Prep for nctree
    # only illumina input and no PE
    if illumina_input != "" and nanopore_input == "" and paired_end == False:
        for i in range(len(illumina_input)):
            openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + illumina_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
    # only illumina input and PE
    elif illumina_input != "" and nanopore_input == "" and paired_end == True:
        for i in range(0, len(illumina_input), 2):
            openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + illumina_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
    # only nanopore
    elif nanopore_input != "" and illumina_input == "":
        for i in range(len(nanopore_input)):
            openname = target_dir + nanopore_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + nanopore_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
    # Both illumina and nanopore input and no PE
    elif illumina_input != "" and nanopore_input != "" and paired_end == False:
        for i in range(len(illumina_input)):
            openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + illumina_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
        for i in range(len(nanopore_input)):
            openname = target_dir + nanopore_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + nanopore_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
    # Bpth illumina and nanopore input and PE
    elif illumina_input != "" and nanopore_input != "" and paired_end == True:
        for i in range(0, len(illumina_input), 2):
            openname = target_dir + illumina_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + illumina_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
        for i in range(len(nanopore_input)):
            openname = target_dir + nanopore_input[i] + "_mapping_results.fsa"
            readfile = open(openname, 'r')
            for line in readfile:
                line = line.rstrip()
                if line[0] == ">":
                    print(">" + nanopore_input[i], file=nctreefile)
                else:
                    print(line, file=nctreefile)
    nctreefile.close()

def replace_original_names(output_name, target_dir):
    # replace names

    infile = open(target_dir + 'nctree_input', 'r')
    writefile = open(target_dir + 'writefile', 'w')
    samplecount = 100
    namedict = dict()
    for line in infile:
        if line[0] == ">":
            samplecount += 1
            name_x = ">t" + str(samplecount) + str(samplecount)
            print(name_x, file=writefile)
            namedict[name_x[1:]] = line.rstrip()[1:]
        else:
            print(line.rstrip(), file=writefile)
    infile.close()
    writefile.close()
    #Måske her outputfilenfejen er
    #cmd = "mv nctree_input " + output_name
    #os.system(cmd)
    cmd = "mv " + target_dir  + "writefile " + target_dir + "nctree_input"
    os.system(cmd)
    return namedict

def nctreeFunction(ncfile, target_dir, logfile):
    t0 = time.time()
    #
    #
    #
    etta = 0.001
    #
    # Parse command line options

    inputfile = target_dir + ncfile
    outputfile = target_dir + ncfile + "_matrix"
    difffilename = target_dir + "difffile"
    allcalled = True
    #
    # Open files
    #
    #
    # File with reads
    #
    if inputfile != None:
        inputfile = open(inputfile, "r")
    else:
        inputfile = sys.stdin
    #
    # File for general output
    #
    if outputfile != None:
        outputfile = open(outputfile, "w")
    else:
        outputfile = sys.stdout
    #
    # File for differences between samples
    #
    if difffilename != None:
        difffile = open(difffilename, "w")
    #
    # Read Input fasta file
    #
    inputseq = []
    inputseqsegments = []
    consensusseq = []
    inputname = []
    inputdesc = []
    Ninputs = 0
    i = 0
    # if inputfile != None:
    if 1 != 0:
        # allways true
        t1 = time.time()
        # sys.stdout.write("%s %d %s\n" % ("# Time used: ", int(t1-t0)," seconds"))
        sys.stdout.write("%s\n" % ("# Reading inputfile"))
        print ("%s" % ("# Nctree Data: "), file=logfile)
        for line in inputfile:
            fields = line.split()
            if len(line) > 1:
                if fields[0][0] == ">":
                    # print "# input ",line
                    if (i > 0):
                        inputseq[-1] = ''.join(inputseqsegments)
                        # print len(inputseq),len(inputseq[-1]),len(inputseq[len(inputseq)-1])
                    del inputseqsegments
                    inputseqsegments = []
                    i = 0
                    inputseq.append("")
                    consensusseq.append("")
                    inputname.append(fields[0][1:])
                    inputdesc.append(re.sub(r"^[^\s]+\s", "", line.strip()))
                else:
                    # inputseq[-1] = inputseq[-1]  + fields[0]
                    # print i
                    # print fields[0]
                    inputseqsegments.append("")
                    inputseqsegments[i] = fields[0]
                    i += 1
        inputseq[-1] = ''.join(inputseqsegments)
        # print len(inputseq),len(inputseq[-1]),len(inputseq[len(inputseq)-1])
    del inputseqsegments

    #
    # Cast sequences in numpy datastructure
    #
    nseq = len(inputseq)
    lseq0 = len(inputseq[0])
    nchrom = 1
    lseqmax = lseq0
    while (len(inputseq[nchrom]) != lseq0):
        sys.stdout.write("# Length of chromosome %d: %d\n" % (nchrom, len(inputseq[nchrom - 1])))
        print ("# Length of chromosome %d: %d" % (nchrom, len(inputseq[nchrom - 1])), file=logfile)
        if (len(inputseq[nchrom]) > lseqmax):
            lseqmax = len(inputseq[nchrom])
        nchrom += 1
    sys.stdout.write("# Length of chromosome %d: %d\n" % (nchrom, len(inputseq[nchrom - 1])))
    print ("# Length of chromosome %d: %d" % (nchrom, len(inputseq[nchrom - 1])), file=logfile)
    nstrain = int(nseq / nchrom)
    sys.stdout.write("# Number of strains: %d\n" % (nstrain))
    print ("# Number of strains: %d" % (nstrain), file=logfile)
    sys.stdout.write("# Number of chromosomes: %d\n" % (nchrom))
    print ("# Number of chromosomes: %d" % (nchrom), file=logfile)
    # for h in range(0, nchrom):
    inputseqmat = np.zeros((nseq, lseqmax), dtype=np.int8)
    non_nucleotidemat = np.zeros((nseq, lseqmax), dtype=np.int8)

    #
    # Define nucleotides as numbers
    #
    nuc2num = {
        #
        # A  adenosine          C  cytidine             G  guanine
        # T  thymidine          N  A/G/C/T (any)        U  uridine
        # K  G/T (keto)         S  G/C (strong)         Y  T/C (pyrimidine)
        # M  A/C (amino)        W  A/T (weak)           R  G/A (purine)
        # B  G/T/C              D  G/A/T                H  A/C/T
        # V  G/C/A              -  gap of indeterminate length
        #   A C G T
        # A A M R W
        # C M C S Y
        # G R S G K
        # T W Y K T
        #
        'A': 1,
        'T': 2,
        'C': 3,
        'G': 4,
        'M': 5,
        'R': 6,
        'W': 7,
        'S': 8,
        'Y': 9,
        'K': 10
    }
    #
    # Cast sequences as numpy vectors
    #
    t1 = time.time()
    sys.stdout.write("%s %d %s\n" % ("# Time used: ", int(t1 - t0), " seconds"))
    sys.stdout.write("%s\n" % ("# Cast input sequences in numpy"))
    #
    # Find non nucleotide positions
    #
    if allcalled != None:
        for i in range(0, nseq):
            for j in range(0, len(inputseq[i])):
                try:
                    # Set A, T, C, G to 1, 2, 3, 4, respectively (vector is initialized to 0)
                    inputseqmat[i][j] = nuc2num[inputseq[i][j]]
                except:
                    # Set to 1 if position do not contain an A, T, C or G (vector is initialized to 0)
                    non_nucleotidemat[i][j] = 1
    #
    # Keep only positions which are called in all sequences - this code is commented out
    #
    for n in range(0, nchrom):
        bad = 0
        sys.stdout.write("# Chromosome: %d\n" % (n + 1))
        print ("# Chromosome: %d" % (n + 1), file=logfile)
        for j in range(0, len(inputseq[n])):
            # print "pos ",j
            for l in range(0, nstrain):
                # print "strain ",l
                i = n + l * nchrom
                try:
                    # Set A, T, C, G to 1, 2, 3, 4, respectively (vector is initialized to 0)
                    inputseqmat[i][j] = nuc2num[inputseq[i][j]]
                except:
                    # Set to 1 if position do not contain an A, T, C or G (vector is initialized to 0)
                    non_nucleotidemat[i][j] = 1
                    #
                    # if options.extendtemplate != None:
                    #
                    if allcalled != None:
                        # print n,j,l, inputseq[i][j]
                        bad += 1
                        for l in range(0, nstrain):
                            i = n + l * nchrom
                            inputseqmat[i][j] = 0
                            non_nucleotidemat[i][j] = 1
                        break
        if allcalled != None:
            sys.stdout.write(
                "# Number of positions used for phylogeny in chromosome %d: %d\n" % (n + 1, len(inputseq[n]) - bad))
            print ("# Number of positions used for phylogeny in chromosome %d: %d" % (n + 1, len(inputseq[n]) - bad), file=logfile)

    # print bad

    #
    # Calculate pairwise distances
    #
    t1 = time.time()
    sys.stdout.write("%s %d %s\n" % ("# Time used: ", int(t1 - t0), " seconds"))
    print ("%s %d %s" % ("# Time used: ", int(t1 - t0), " seconds"), file=logfile)
    sys.stdout.write("%s\n" % ("# Calculating pairwise distances"))
    mat = np.zeros((nstrain, nstrain))
    prog = 0

    if difffile == None:
        #
        # fast calculation not saving different positions
        #
        for l in range(0, nstrain):
            for m in range(0, l):
                for n in range(0, nchrom):
                    i = l * nchrom + n
                    j = m * nchrom + n
                    # for j in range(0, i):
                    prog += 1
                    dist = np.sum(inputseqmat[i] != inputseqmat[j]) - np.sum(
                        non_nucleotidemat[i] != non_nucleotidemat[j])
                    # calledi = np.sum(inputseqmat[i]!=0)
                    # calledj = np.sum(inputseqmat[j]!=0)
                    # chromlength = len(inputseq[i])
                    #
                    # Estimate genetic distance if all bases had been called in both sequences
                    #
                    # scalefactor = float((chromlength*chromlength)/(calledi*calledj+0.001))
                    # print "l: ",l,"m: ",m,"n: ",n,"dist: ",dist,"mat: ",mat[l][m]
                    mat[l][m] += dist
                    # mat[l][m] += dist*scalefactor
                    mat[m][l] = mat[l][m]
                # print "l: ",l,"m: ",m,"i: ",i,"n: ",n,"j: ",j, "dist: ", dist, "sumdist: ", mat[l][m], "Calledi: ", calledi, "calledj: ",calledj, "len: ", len(inputseq[i]), "dist: ", dist, "scalefactor: ", scalefactor,"mat: ", mat[l][m]
            # sys.stdout.write("\r# %s%s done" % (int(2*100*prog/(nseq*nseq+0.001)),"%"))
            # sys.stdout.flush()
        # sys.stdout.write("\n")


    else:
        #
        # Slow version keeping information about different positions
        # NB this has to be reworked to handle multi chromosome genomes
        #
        for i in range(0, nseq):
            for j in range(0, i):
                prog += 1
                sum = 0
                for k in range(0, lseq0):
                    if (inputseqmat[i][k] != inputseqmat[j][k] and inputseqmat[i][k] > 0 and inputseqmat[j][k] > 0):
                        sum += 1
                        difffile.write("%-8s %-8s %8d %1s %1s\n" % (
                            inputname[i], inputname[j], k + 1, inputseq[i][k], inputseq[j][k]))
                mat[i][j] = sum
                mat[j][i] = mat[i][j]
                sys.stdout.write("\r# %s%s done" % (int(2 * 100 * prog / (nseq * nseq + 0.001)), "%"))
                sys.stdout.flush()
        sys.stdout.write("\n")

    #
    # Write in neighbor format
    #
    outputfile.write("%s\n" % (nstrain))
    for i in range(0, nstrain):
        mynamei = inputname[i * nchrom]
        outputfile.write("%-11s " % (mynamei))
        for j in range(0, nstrain):
            mynamej = inputname[i * nchrom]
            outputfile.write("%0.8f" % (mat[i][j]))
            if (j == nstrain - 1):
                outputfile.write("\n")
            else:
                outputfile.write(" ")
            #
    # Close files
    #
    t1 = time.time()
    sys.stdout.write("%s %d %s\n" % ("# Finishing. Time used: ", int(t1 - t0), " seconds"))
    # inputfile.close()
    # templatefile.close()
    # outputfile.close()

def nctree(ncfile, target_dir, logfile):
    # Nctree
    nctreeFunction(ncfile, target_dir, logfile)
    #cmd = "nctree -i " + target_dir + "nctree_input -o " + target_dir + "infile -d " + target_dir + "difffile -a"
    #os.system(cmd)
    #cmd = "mv difffile " + target_dir
    #os.system(cmd)
    openfile = open(target_dir + ncfile + "_matrix", 'r')
    writefile = open(target_dir + ncfile + "_matrix" + "2", 'w')
    for line in openfile:
        line = line.rstrip()
        line = line.replace("\t", "!?!")
        line = line.replace(" ", "!?!")
        line = line.replace("!?!!?!!?!!?!", "\t")
        line = line.replace("!?!", "\t")
        line = line.split("\t")
        if len(line) > 1:
            for i in range(len(line)-1):
                number = line[1+i]
                number = float(number)
                number = int(round(number))
                number = str(number)
                line[1+i] = number
        line = "\t".join(line)
        print (line, file=writefile)

    cmd = "rm " + target_dir + ncfile + "_matrix"
    os.system(cmd)
    cmd = "mv " + target_dir + ncfile + "_matrix" + "2 " + target_dir + ncfile + "_matrix"
    os.system(cmd)
    openfile.close()
    writefile.close()

    #cmd = "mv " + target_dir + infile + " "+ target_dir + infile +  "_matrix"
    #os.system(cmd)


def ccphylo(ncfile, output_name, target_dir):
    # Neighbor
    cmd = "ccphylo tree -i " + target_dir + ncfile + "_matrix" + " -o "+ target_dir + ncfile +"_outtree"
    os.system(cmd)
    #cmd = "mv outtree " + target_dir
    #os.system(cmd)
    #Remaining samples with original names

def rename_reads(target_dir):
    # Renaming samples
    # Cleaning

    cmd = "mv " + target_dir + "infile " + target_dir + "matrix"
    os.system(cmd)
    #cmd = "rm " + target_dir + "template_kma_results.spa"
    #os.system(cmd)


def save_files( target_dir, illumina_input, nanopore_input, paired_end, reference):
    save_files_bool = True
    if save_files_bool == False:
        if illumina_input != "" and paired_end == False:
            for i in range(len(illumina_input)):
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.aln"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.frag.gz"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.res"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.fsa"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)
        elif illumina_input != "" and paired_end == True:
            for i in range(0, len(illumina_input), 2):
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.aln"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.frag.gz"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.res"
                os.system(cmd)
                cmd = "rm " + target_dir + illumina_input[i] + "_mapping_results.fsa"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)
        if nanopore_input != "":
            for i in range(len(nanopore_input)):
                cmd = "rm " + target_dir + nanopore_input[i] + "_mapping_results.aln"
                os.system(cmd)
                cmd = "rm " + target_dir + nanopore_input[i] + "_mapping_results.frag.gz"
                os.system(cmd)
                cmd = "rm " + target_dir + nanopore_input[i] + "_mapping_results.res"
                os.system(cmd)
                cmd = "rm " + target_dir + nanopore_input[i] + "_mapping_results.fsa"
                os.system(cmd)
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)
    elif save_files_bool == True:
        if illumina_input != "" and paired_end == False:
            for i in range(len(illumina_input)):
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.aln" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.frag.gz" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.res" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.fsa" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)
        elif illumina_input != "" and paired_end == True:
            for i in range(0, len(illumina_input), 2):
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.aln" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.frag.gz" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.res" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.fsa" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + illumina_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)
        if nanopore_input != "":
            for i in range(len(nanopore_input)):
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.aln" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.frag.gz" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.res" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.fsa" + " " + target_dir +"DataFiles"
                os.system(cmd)
                cmd = "mv " + target_dir + nanopore_input[i] + "_mapping_results.vcf.gz " + target_dir + "DataFiles"
                os.system(cmd)

    if reference != "":
        cmd = "rm " + target_dir + "temdb.comp.b"
        os.system(cmd)
        cmd = "rm " + target_dir + "temdb.index.b"
        os.system(cmd)
        cmd = "rm " + target_dir + "temdb.length.b"
        os.system(cmd)
        cmd = "rm " + target_dir + "temdb.name"
        os.system(cmd)
        cmd = "rm " + target_dir + "temdb.seq.b"
        os.system(cmd)

def load_illumina(illumina_path_input):
    if illumina_path_input != "":
        path = illumina_path_input
        illumina_files = os.listdir(path)
        illumina_files.sort()
    else:
        illumina_files = ""
    return illumina_files

def load_nanopore(nanopore_path_input):
    if nanopore_path_input != "":
        path = nanopore_path_input
        nanopore_files = os.listdir(path)
        nanopore_files.sort()
    else:
        nanopore_files = ""
    return nanopore_files

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
    if len(total_input_files) < 3:
        if appendRun == False:
            sys.exit("You have given less than 3 files to analyze. Please run the program again with more datafiles.")
    total_input_files = " ".join(total_input_files)
    return total_input_files

def logfileConditions(logfile, surveillanceRun):
    logdict = {}
    if args.dcmMethylation != "":
        logdict['dcmMethylation'] = args.dcmMethylation
    else:
        logdict['dcmMethylation'] = ""
    if args.prune != False:
        logdict['prune'] = str(args.prune)
    else:
        logdict['prune'] = str(False)
    if args.prune_distance != 10:
        logdict['prune_distance'] = args.prune_distance
    else:
        logdict['prune_distance'] = 10
    if args.bc != 0.7:
        logdict['bc'] = args.bc
    else:
        logdict['bc'] = 0.7
    if args.ref_kma_database != "":
        logdict['ref_kma_database'] = args.ref_kma_database
    else:
        logdict['ref_kma_database'] = ""
    if args.multi_threading != 1:
        logdict['multi_threading'] = args.multi_threading
    else:
        logdict['multi_threading'] = 1
    if surveillanceRun == False:
        if args.reference != "":
            logdict['reference'] = args.reference
        else:
            logdict['reference'] = ""
    if args.output_path != "":
        logdict['output_path'] = args.output_path
    else:
        logdict['output_path'] = ""
    if args.output_name != "":
        logdict['output_name'] = args.output_name
    else:
        logdict['output_name'] = ""
    if args.paired_end != False:
        logdict['paired_end'] = str(args.paired_end)
    else:
        logdict['paired_end'] = str(False)
    print (logdict, file=logfile)

def researchPipeline(i_path_illumina, i_path_nanopore, paired_end, dcmMethylation, prune, prune_distance, bc, ref_kma_database, multi_threading, reference, output_path, output_name, appendRun, surveillanceRun, researchRun):

    if i_path_illumina == "" and i_path_nanopore == "":
        sys.exit("You did not give any input. Run the program again with an input")
    if output_path == "":
        current_path = os.getcwd()
        target_dir = current_path + "/" + output_name + "/"
        cmd = "mkdir " + output_name
        os.system(cmd)
    else:
        new_dir = output_path + output_name
        cmd = "mkdir " + new_dir
        os.system(cmd)
        target_dir = output_path + output_name + "/"
    kma_database_path = ref_kma_database



    logfilename = target_dir + "logfile_" + output_name
    logfile = open(logfilename, 'w')
    cmd = "mkdir " + target_dir + "DataFiles"
    os.system(cmd)

    #Count for multifastFiles
    multiFastaCount =  0

    # Print messages
    startTime = time.time()
    print("# Running MinION-Typer 1.0.0 with following input conditions:", file=logfile)
    logfileConditions(logfile, surveillanceRun)
    if paired_end == True:
        print("# -pe", file=logfile)
    if prune == True:
        print("# -prune", file=logfile)
        print("# -prune_distance: " + str(prune_distance), file=logfile)
    if bc != 0:
        print("# -bc: " + str(bc), file=logfile)
    if ref_kma_database != "":
        print("# -db: " + ref_kma_database, file=logfile)
    if multi_threading != 1:
        print("# -thread: " + str(multi_threading), file=logfile)
    if reference != "":
        print("# -ref: " + reference, file=logfile)

    illumina_files = load_illumina(i_path_illumina)
    nanopore_files = load_nanopore(i_path_nanopore)
    complete_path_illumina_files = generate_complete_path_illumina_files(illumina_files, i_path_illumina)
    complete_path_nanopore_files = generate_complete_path_nanopore_files(nanopore_files, i_path_nanopore)
    total_filenames = combine_input_files(complete_path_illumina_files, complete_path_nanopore_files)
    best_template = find_best_template(total_filenames, target_dir, kma_database_path, logfile, surveillanceRun, researchRun, appendRun)[0]
    print (best_template)
    mapping_illumina(complete_path_illumina_files, illumina_files, paired_end, best_template, target_dir, kma_database_path, logfile, multi_threading, surveillanceRun)
    mapping_nanopore(complete_path_nanopore_files, nanopore_files, best_template, target_dir, kma_database_path, logfile, multi_threading, surveillanceRun)
    MultiFasta(illumina_files, nanopore_files, paired_end, target_dir, multiFastaCount)
    print("The original mapped reads produced by KMA (pre-pruning, dcm-methylation etc is saved in the file named original_mappings_multi.fsa", file=logfile)
    print("The mapped reads post pruning, dcm-methylation etc is saved in the file called nctree_input. This is the multiFasta file from which the distance matrix was calculated from.", file=logfile)
    multiFastaCount  += 1
    if prune == True:
        prune_nanopore(prune, nanopore_files, target_dir, prune_distance)
    if prune == True:
        prune_illumina(prune, paired_end, illumina_files, target_dir, prune_distance)
    #dcm start
    dcmfilename = target_dir + "dcmMethylationPositions"
    starttimedcm = time.time()
    dcmMethylationFunction(dcmMethylation, nanopore_files, illumina_files, target_dir, logfile, dcmfilename, paired_end)
    endtimedcm = time.time()
    finaltime = endtimedcm - starttimedcm
    print("runtime dcm: " + str(finaltime), file=logfile)
    #dcm end
    MultiFasta(illumina_files, nanopore_files, paired_end, target_dir, multiFastaCount)
    if appendRun == True:
        cmd = "cat nctree_input " + output_name + "/nctree_input > " + output_name + "/merged_nctree_input"
        os.system(cmd)
        ncname = "merged_nctree_input"
    elif appendRun == False: #IF appendPipeline is not running
        ncname = "nctree_input"
    nctree(ncname, target_dir, logfile)
    ccphylo(ncname, output_name, target_dir)
    save_files(target_dir, illumina_files, nanopore_files, paired_end, reference)
    endTime = time.time()
    dTime = endTime-startTime
    print ("MinION-Typer total runtime: " + str(dTime) + " seconds", file=logfile)
    logfile.close()


def appendPipeline(input_illumina_files, input_nanopore_files, output_name, paired_end, output_path, appendRun, surveillanceRun, researchRun):
    if appendRunLogFile == "":
        sys.exit("You did not enter a logfile from a previous MinIonTyper run. If you wish to append new mappings to a previously calculated matrix, then you must supply the relevant logfile")
    f = open(appendRunLogFile, 'r')
    lines = f.readlines()[1].rstrip()
    f.close()
    d = lines.replace("'", "\"")
    logdict = json.loads(d)
    i_path_illumina = input_illumina_files
    i_path_nanopore = input_nanopore_files
    reference = ""
    paired_end = paired_end
    dcmMethylation = logdict['dcmMethylation']
    prune = logdict['prune']
    prune_distance = logdict['prune_distance']
    bc = logdict['bc']
    ref_kma_database = logdict['ref_kma_database']
    multi_threading = logdict['multi_threading']
    reference = logdict['reference']
    original_output_path = logdict['output_path']
    original_output_name = logdict['output_name']
    new_output_path = logdict['output_path']
    new_output_name = original_output_name + output_name
    researchPipeline(i_path_illumina, i_path_nanopore, args.paired_end, dcmMethylation, prune,
               prune_distance, bc, ref_kma_database, multi_threading, reference, new_output_path,
               new_output_name)
    print ("appending complete")

def SurveillancePipeline(i_illumina, i_nanopore, paired_end, dcmMethylation, prune, prune_distance, bc, ref_kma_database, multi_threading, output_path, output_name, appendRun, surveillanceRun, researchRun, isolate_database, isolate_storage, reference_storage):
    if i_illumina == "" and i_nanopore == "":
        sys.exit("You did not give any input. Run the program again with an input")
    if output_path == "":
        current_path = os.getcwd()
        target_dir = current_path + "/" + output_name + "/"
        cmd = "mkdir " + output_name
        os.system(cmd)
    else:
        new_dir = output_path + output_name
        cmd = "mkdir " + new_dir
        os.system(cmd)
        target_dir = output_path + output_name + "/"
    kma_database_path = ref_kma_database

    logfilename = target_dir + "logfile_" + output_name
    logfile = open(logfilename, 'w')
    cmd = "mkdir " + target_dir + "DataFiles"
    os.system(cmd)

    reference = ""

    # Count for multifastFiles
    multiFastaCount = 0

    # Print messages
    startTime = time.time()
    print("# Running MinION-Typer 1.0.0 with following input conditions:", file=logfile)
    logfileConditions(logfile, surveillanceRun)
    if paired_end == True:
        print("# -pe", file=logfile)
    if prune == True:
        print("# -prune", file=logfile)
        print("# -prune_distance: " + str(prune_distance), file=logfile)
    if bc != 0:
        print("# -bc: " + str(bc), file=logfile)
    if ref_kma_database != "":
        print("# -db: " + ref_kma_database, file=logfile)
    if multi_threading != 1:
        print("# -thread: " + str(multi_threading), file=logfile)
    if reference != "":
        print("# -ref: " + reference, file=logfile)
    '''
    if i_path_illumina != "" or i_path_nanopore != "":
        illumina_files = load_illumina(i_path_illumina)
        nanopore_files = load_nanopore(i_path_nanopore)
        complete_path_illumina_files = generate_complete_path_illumina_files(illumina_files, i_path_illumina)
        complete_path_nanopore_files = generate_complete_path_nanopore_files(nanopore_files, i_path_nanopore)
        total_filenames = combine_input_files(complete_path_illumina_files, complete_path_nanopore_files, surveillanceRun, researchRun, appendRun)
    '''
    if len(i_illumina) == 1:
        illumina_files = i_illumina[0]
    elif len(i_illumina) == 2:
        illumina_files = i_illumina[0] + " " + i_illumina[1]
    else:
        illumina_files = ""
    nanopore_files = i_nanopore

    illumina_assembly = ""
    nanopore_assembly = ""

    if i_illumina != "" and i_nanopore != "":
        total_filenames = illumina_files + " " + nanopore_files
        sys.exit("Please only give one file at a time for the surveillance pipeline.")
    elif illumina_files != "":
        total_filenames = illumina_files
        nanopore_files = ""
        illumina_assembly = True
    elif nanopore_files != "":
        total_filenames = nanopore_files
        illumina_files = ""
        nanopore_assembly = True

    best_template, best_template_score, no_template_found, templatename = find_best_template(total_filenames, target_dir, kma_database_path, logfile, surveillanceRun, researchRun, appendRun)
    if i_illumina != "":
        if i_illumina[0][0] == "/":
            illumina_output = i_illumina[0].split("/")[-1]
        else:
            illumina_output = i_illumina[0]
    if i_nanopore != "":
        if i_nanopore[0] == "/":
            nanopore_output = i_nanopore[0].split("/")[-1]
        else:
            nanopore_output = i_nanopore

    if total_filenames[0] == "/":
        total_filenames = total_filenames.split("/")[-1]
    print (best_template)
    print ("Score of the best template was: " + str(best_template_score))

    #cmd = "mv " + target_dir + illumina_output + "_assembly/scaffolds.fasta" + " " + reference_storage + illumina_output + ".assembled"
    #os.system(cmd)

    ref_db_name = ref_kma_database.split("/")[-1]
    ref_db_path = kma_database_path[:-len(ref_db_name)]

    if no_template_found == True:
        if illumina_assembly == True:
            if paired_end == True:
                cmd = "unicycler -1 {} -2 {} -o {} ".format(i_illumina[0], i_illumina[1], target_dir + illumina_output + "_assembly")
                os.system(cmd)
            else:
                cmd = "unicycler -s {} -o {}".format(i_illumina[0], target_dir + illumina_output + "_assembly")
                os.system(cmd)

            # Insert new reference in KMA reference db
            print ("no template TRUE")
            #Unicycler illumina

            """
            to be deleted
            # Assembly of illumina
            if paired_end == False:
                cmd = "spades.py -s " + i_illumina[0] + " -o " + target_dir + illumina_output + "_assembly"
                os.system(cmd)
            elif paired_end == True:
                total_filenames = i_illumina[0]
                cmd = "spades.py -1 " + i_illumina[0] + " -2 " + i_illumina[
                    1] + " -o " + target_dir + illumina_output + "_assembly"
                os.system(cmd)
            """

            # concatenate all reads into one file
            #Look into clear method
            infile = open(target_dir + illumina_output + "_assembly/assembly.fasta", 'r')
            writefile = open(target_dir + illumina_output + ".assebmled", 'w')
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line
            print (">" + illumina_output, file = writefile)
            print (sequence, file = writefile)
            print (len(sequence))
            infile.close()
            writefile.close()

            cmd = "rm {}".format(target_dir + illumina_output + "_assembly/assembly.fasta")
            print (cmd)
            os.system(cmd)

            cmd = "kma index -t_db " + ref_kma_database + " -i " + target_dir + illumina_output + ".assebmled"
            print(cmd)
            os.system(cmd)

            cmd = "cp " + target_dir + illumina_output + ".assebmled " + ref_db_path + "references/" + illumina_output + ".assebmled"
            print(cmd)
            os.system(cmd)
            conn = sqlite3.connect(isolate_database)
            c = conn.cursor()

            dbstring = "INSERT INTO refs(refName) VALUES ('{}')".format(total_filenames)

            #dbstring = "INSERT INTO refs(refName) VALUES ('" + total_filenames + "')"
            c.execute(dbstring)
            conn.commit()
            conn.close()

            sys.exit("No template was found, so input was added to references")
        elif nanopore_assembly == True:
            # Insert new reference in KMA reference db
            print ("no template TRUE runnning nanopore assembly")
            # Longread assembly

            cmd = "unicycler -l {} -o {}".format(nanopore_files, target_dir + nanopore_output + "_assembly")
            os.system(cmd)

            infile = open(target_dir + nanopore_output + "_assembly/assembly.fasta", 'r')
            writefile = open(target_dir + nanopore_output + ".assebmled", 'w')
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line
            print(">" + nanopore_output, file=writefile)
            print(sequence, file=writefile)
            print(len(sequence))
            infile.close()
            writefile.close()

            cmd = "rm {}".format(target_dir + nanopore_output + "_assembly/assembly.fasta")
            os.system(cmd)

            cmd = "kma index -t_db " + ref_kma_database + " -i " + target_dir + nanopore_output + ".assebmled"
            os.system(cmd)

            cmd = "cp " + target_dir + nanopore_output + ".assebmled " + ref_db_path + "references/" + nanopore_output + ".assebmled"
            os.system(cmd)
            conn = sqlite3.connect(isolate_database)
            c = conn.cursor()

            dbstring = "INSERT INTO refs(refName) VALUES ('{}')".format(total_filenames)

            # dbstring = "INSERT INTO refs(refName) VALUES ('" + total_filenames + "')"
            c.execute(dbstring)
            conn.commit()
            conn.close()

            sys.exit("No template was found, so input was added to references")


            
    elif no_template_found == False:

        print ("RUN REST OF KMA")
        print (str(best_template))
        print (str(best_template_score))
        print (templatename)


    print (illumina_files)
    complete_path_illumina_files = []
    complete_path_nanopore_files = []

    if illumina_files != "":
        complete_path_illumina_files = []
        complete_path_illumina_files.append(illumina_files)
        illuminaname = illumina_files.split("/")[-1]
        illumina_files = []
        illumina_files.append(illuminaname)

    if nanopore_files != "":
        complete_path_nanopore_files = []
        complete_path_nanopore_files.append(nanopore_files)
        nanoporename = nanopore_files.split("/")[-1]
        nanopore_files = []
        nanopore_files.append(nanoporename)

    print (illumina_files)
    print (complete_path_illumina_files)
    print (nanopore_files)
    print (complete_path_nanopore_files)

    mapping_illumina(complete_path_illumina_files, illumina_files, paired_end, best_template, target_dir,
                     kma_database_path, logfile, multi_threading, surveillanceRun)
    mapping_nanopore(complete_path_nanopore_files, nanopore_files, best_template, target_dir, kma_database_path,
                     logfile, multi_threading, surveillanceRun)
    print ("FINISHED MAPPING")
    MultiFasta(illumina_files, nanopore_files, paired_end, target_dir, multiFastaCount)


    print(
    "The original mapped reads produced by KMA (pre-pruning, dcm-methylation etc is saved in the file named original_mappings_multi.fsa",
    file=logfile)
    print(
    "The mapped reads post pruning, dcm-methylation etc is saved in the file called nctree_input. This is the multiFasta file from which the distance matrix was calculated from.",
    file=logfile)
    multiFastaCount += 1
    if prune == True:
        prune_nanopore(prune, nanopore_files, target_dir, prune_distance)
    if prune == True:
        prune_illumina(prune, paired_end, illumina_files, target_dir, prune_distance)

    print ("FINISHED PRUNING")
    # dcm start
    dcmfilename = target_dir + "dcmMethylationPositions"
    starttimedcm = time.time()
    dcmMethylationFunction(dcmMethylation, nanopore_files, illumina_files, target_dir, logfile, dcmfilename)
    endtimedcm = time.time()
    finaltime = endtimedcm - starttimedcm
    print("runtime dcm: " + str(finaltime), file=logfile)
    # dcm end
    MultiFasta(illumina_files, nanopore_files, paired_end, target_dir, multiFastaCount)
    #if appendRun == True:
    #    cmd = "cat nctree_input " + output_name + "/nctree_input > " + output_name + "/merged_nctree_input"
    #    os.system(cmd)
    #    ncname = "merged_nctree_input"
    #elif appendRun == False:  # IF appendPipeline is not running
    #    ncname = "nctree_input"
    #nctree(ncname, target_dir, logfile)
    #ccphylo(ncname, output_name, target_dir)
    #save_files(target_dir, illumina_files, nanopore_files, paired_end, reference)


    ####
    cmd = "cp " + target_dir + "nctree_input" + " " + ref_db_path + "/isolates_mappings/" + illuminaname
    os.system(cmd)

    conn = sqlite3.connect(isolate_database)
    c = conn.cursor()


    dbstring = "INSERT INTO isolates(refName, isolateName) VALUES ('" + templatename + "', '" + illuminaname + "')"

    print (dbstring)

    # dbstring = "INSERT INTO refs(refName) VALUES ('" + total_filenames + "')"
    c.execute(dbstring)
    conn.commit()

    c.execute("SELECT refName, isolateName from isolates")
    print (c.fetchall())

    conn.close()

    ###

    endTime = time.time()
    dTime = endTime - startTime
    print ("MinION-Typer total runtime: " + str(dTime) + " seconds", file=logfile)
    logfile.close()


def main():
    surveillanceRun = False
    researchRun = False
    appendRun = False
    if sys.argv[1].upper() == "SURVEILLANCE":
        surveillanceRun = True
        SurveillancePipeline(args.i_illumina, args.i_nanopore, args.paired_end, args.dcmMethylation, args.prune, args.prune_distance, args.bc, args.ref_kma_database, args.multi_threading, args.output_path, args.output_name, appendRun, surveillanceRun, researchRun, args.isolate_database, args.isolate_storage, args.reference_storage)
    elif sys.argv[1].upper() == "RESEARCH":
        researchRun = True
        researchPipeline(args.i_path_illumina, args.i_path_nanopore, args.paired_end, args.dcmMethylation, args.prune, args.prune_distance, args.bc, args.ref_kma_database, args.multi_threading, args.reference, args.output_path, args.output_name, appendRun, surveillanceRun, researchRun)
    elif sys.argv[1].upper() == "APPEND":
        appendRun = True
        appendPipeline(args.i_path_illumina, args.i_path_nanopore, args.output_name, args.paired_end, args.output_path, appendRun, surveillanceRun, researchRun)
    '''
    if appendRun == True:
        appendPipeline(args.i_path_illumina, args.i_path_nanopore, args.output_name, args.paired_end, args.output_path)
    elif args.researchPipeline == True:
        researchPipeline(args.i_path_illumina, args.i_path_nanopore, args.paired_end, args.dcmMethylation, args.prune, args.prune_distance, args.bc, args.ref_kma_database, args.multi_threading, args.reference, args.output_path, args.output_name)
    else:
        bacterialSurveillancePipeline()
    '''
if __name__== "__main__":
  main()


'''
parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-i_path_illumina', action="store", type=str, dest='i_path_illumina', default="", help='The path to the directory containing ONLY the input illumina files. Should be used when analyzing >5 read-files at a time.')
parser.add_argument('-i_path_nanopore', action="store", type=str, dest='i_path_nanopore', default="", help='The path to the directory containing ONLY the input nanopore files. Should be used when analyzing >5 read-files at a time.')
parser.add_argument("-pe", action="store_true", dest="paired_end", help="If paipred ends are used give input as True (-pe True). If Paired-ends are used, it is important that the files are written in the correct order, such as: sample1_1.fasta sample1_2.fasta sample2_1.fasta sample2_1.fasta")
parser.add_argument("-dcmMethylation", type=str, action="store", dest="dcmMethylation", default="", help="Will mask the dcmMethylation patterns matching CC[X]GG, where X will be ")
parser.add_argument("-prune", action="store_true", dest="prune", help="If set to true, all SNPs that are located within 10 bp will not be included")
parser.add_argument("-prune_distance", type=int, action="store", dest="prune_distance", default=10, help="X lenght that SNPs can be located between each other. Default is 10. If two SNPs are located within X lenght of eachother, everything between them as well as X lenght on each side of the SNPs will not be used in the alignments to calculate the distance matrix.")
#parser.add_argument("-save_individual_files", action="store_true", dest="save_individual_files", help="Set to True if you want to keep the original individual  mapping results. Otherwise the will only be compiled into a multi fasta file ")
parser.add_argument("-bc", action="store", type=float, default = 0.7, dest="bc", help="Base calling parameter for nanopore KMA mapping. Default is 0.7")
parser.add_argument("-db", action="store", type=str, default = "", dest="ref_kma_database", help="Comeplete path for the ref_kma_database for KMA mapping")
parser.add_argument("-thread", action="store", default = 1, dest="multi_threading", help="Set this parameter to x-number of threads that you would like to use during KMA-mapping.")
parser.add_argument("-ref", action="store", type=str, default = "", dest="reference", help="KMA will by default determine the best template against the given database. However, if you want to align your query sequences against a reference of your own choice, use this function. If this is left blank, KMA will determine the optimal reference.")
parser.add_argument("-appendPipeline", action="store", type=str, default = "", dest="appendPipeline", help="appendPipeline")
parser.add_argument("-appendPipelineLogFile", action="store", type=str, default = "", dest="appendPipelineLogFile", help="appendPipelineFile")
parser.add_argument("-o_path", action="store", type=str, default="", dest="output_path", help="If you would like your output directory to be located in a specific place, use this function. If this function is not used, the output folder will be placed in the working directory. Remember your stated output_directory must end on a dash! Also, remember that this is only the path to the output directory, so the name of your output directory must also be stated using the -o function. An example of correct use of this would be : -o_path /home/user/myDirectory/ -o myNewDirectory ")
parser.add_argument('-version', action='version', version='MinION-Typer 2.0.2', help = "current version of MinION-Typer")
parser.add_argument("-o", action="store", dest="output_name", help="Name that you would like the output directory to be called.")
args = parser.parse_args()
'''

#Big missing: Atm genberegnes distmatrix altid ved append. Kig på egen implementation af nctree hvor rækken kan adderes så n-1Xn-1 matricen ikke kan regnes hele tiden.
"""
eventual conda env:
-anaconda
-unicycler
-racon
-kma
-ccphylo?
-samtools ( for unicycler)
conda install -c conda-forge -c bioconda samtools bzip2
conda forge?

conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge


"""