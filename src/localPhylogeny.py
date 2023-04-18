import os
import sys

def local_phylogeny_from_input_and_database(input, database, specie):
    """Runs local phylogeny from input and database"""
    reference_species = list()
    with open(database + ".name", 'r') as f:
        for line in f:
            if specie in line:
                reference_species.append(line.rstrip().split(' ')[0])
    print (reference_species)
    print (len(reference_species))