import os
import sys
import datetime
from fpdf import FPDF
import dataframe_image as dfi
import pandas as pd
import json
import csv
def prepare_alignment_pdf(bacterial_parser):
    if not os.path.exists(bacterial_parser.data.target_dir + "/pdf_resources"):
        os.mkdir(bacterial_parser.data.target_dir + "/pdf_resources")
    file_list = ["/opt/LPF_databases/resfinder_db/phenotypes.txt",
                 "/opt/LPF_databases/virulencefinder_db/notes.txt",
                 ]
    for item in file_list:
        if not os.path.exists(item):
            bacterial_parser.logger.info("File {} does not exist. Could not compile assembly".format(file))
            sys.exit(1)
    make_amr_csv(bacterial_parser)
    make_virulence_csv(bacterial_parser)
    make_plasmid_csv(bacterial_parser)
    output_bacterial_parser(bacterial_parser)

def make_amr_csv(bacterial_parser): #TBD rewrite and remove.
    phenotype = dict()
    infile = open("/opt/LPF_databases/resfinder_db/phenotypes.txt", 'r')
    for line in infile:
        if not line.startswith("Gene_accession"):
            line = line.rstrip().split("\t")
            if line[0] in bacterial_parser.data.resfinder_hits:
                phenotype[line[0]] = [line[1], line[2]]
    csv_data = []
    csv_data.append(("Gene", "Resistance Class", "Phenotype"))
    for item in phenotype:
        csv_data.append([item, phenotype[item][0], phenotype[item][1]])
    with open(bacterial_parser.data.target_dir + "/pdf_resources/amr_data.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)


def make_virulence_csv(bacterial_parser):  #TBD rewrite and remove.
    new_genes = list()
    for item in bacterial_parser.data.virulence_hits:
        new_genes.append(item.split(":")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/LPF_databases/virulencefinder_db/notes.txt", 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1].strip()].append(line[0])
                else:
                    phenotype[line[1].strip()] = [line[0]]

    csv_data = []
    csv_data.append(("Virulence", "Genes"))
    for item in phenotype:
        csv_data.append((item, ", ".join(phenotype[item])))
    with open(bacterial_parser.data.target_dir + "/pdf_resources/virulence_data.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)

def output_bacterial_parser(bacterial_parser):
    with open(bacterial_parser.data.target_dir + "/pdf_resources/bacterial_parser.json", 'w') as f:
        json.dump(bacterial_parser.data.__dict__, f, indent=4)

def make_plasmid_csv(bacterial_parser):
    csv_data = []
    csv_data.append(("Plasmids"))
    for item in bacterial_parser.data.plasmid_hits:
        csv_data.append((item))
    with open(bacterial_parser.data.target_dir + "/pdf_resources/plasmid_data.csv", 'w') as f:
        for item in csv_data:
            print (item, file=f)

def prepare_assembly_pdf(bacterial_parser):
    if not os.path.exists(bacterial_parser.data.target_dir + "/pdf_resources"):
        os.mkdir(bacterial_parser.data.target_dir + "/pdf_resources")
    file_list = ["/opt/LPF_databases/resfinder_db/phenotypes.txt",
                 "/opt/LPF_databases/virulencefinder_db/notes.txt",
                 bacterial_parser.data.target_dir + "/quast_output/report.tsv"
                 ]
    for file in file_list:
        if not os.path.exists(file):
            bacterial_parser.logger.info("File {} does not exist. Could not compile assembly".format(file))
            sys.exit(1)

    csv_data = []
    with open(bacterial_parser.data.target_dir + "/quast_output/report.tsv", 'r') as f:
        for line in f:
            csv_data.append(line.rstrip().split("\t"))
            
    with open(bacterial_parser.data.target_dir + "/pdf_resources/quast_report.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)

    make_amr_csv(bacterial_parser)
    make_virulence_csv(bacterial_parser)
    make_plasmid_csv(bacterial_parser)
    output_bacterial_parser(bacterial_parser)
