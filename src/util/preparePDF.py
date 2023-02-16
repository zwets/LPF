import os
import sys
import datetime
from fpdf import FPDF
import dataframe_image as dfi
import pandas as pd
import json
import csv
def prepare_alignment_pdf(bacterial_parser):
    pass


def make_amr_json(bacterial_parser): #TBD rewrite and remove.
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
    amr_data = {}
    for item in csv_data:
        amr_data[item[0]] = [item[1], item[2]]
    with open(bacterial_parser.data.target_dir + "amr_data.json", 'w') as f:
        json.dump(amr_data, f)

def make_virulence_json(bacterial_parser):  #TBD rewrite and remove.
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
    virulence_data = {}
    for item in csv_data:
        virulence_data[item[0]] = item[1]
    with open(bacterial_parser.data.target_dir + "virulence_data.json", 'w') as f:
        json.dump(virulence_data, f)

def prepare_assembly_pdf(bacterial_parser):
    file_list = []
    for file in file_list:
        if not os.path.exists(file):
            bacterial_parser.logger.info("File {} does not exist. Could not compile assembly".format(file))
            sys.exit(1)

    quast_data = {}
    with open(bacterial_parser.data.target_dir + "/quast_output/report.tsv", 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            quast_data[row[0]] = row[1]

    with open(bacterial_parser.data.target_dir + "quast_output.json", 'w') as f:
        json.dump(quast_data, f)

    make_amr_json(bacterial_parser)
    make_virulence_json(bacterial_parser)