import os
import sys

def local_phylogeny_from_input_and_database(input, database, reference_header_text):
    """Runs local phylogeny from input and database"""
    specie = reference_header_text.split(' ')[1] + ' ' + reference_header_text.split(' ')[2]
    reference_species = list()
    with open(database + ".name", 'r') as f:
        for line in f:
            if specie in line:
                reference_species.append(line.rstrip().split(' ')[0])
    print (reference_species)
    print (len(reference_species))