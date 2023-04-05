import sys
import logging
def derive_mlst_species(reference_header_text):
    specie = reference_header_text.split(' ')[1] + ' ' + reference_header_text.split(' ')[2]
    mlst_species = reference_header_text.split(' ')[1][0].lower() + reference_header_text.split(' ')[2].lower()
    with open("/opt/LPF_databases/mlst_db/config", 'r') as infile:
        for line in infile:
            if line[0] != "#":
                line = line.split("\t")
                if mlst_species == line[0]:
                    return specie, mlst_species
    return specie, None
def get_mlst(species, genes):
    """Returns the mlst results"""
    with open("/opt/LPF_databases/mlst_db/config", 'r') as fd:
        for line in fd:
            if line[0] != "#":
                line = line.rstrip().split("\t")
                if line[0] == species:
                    expected_genes = line[2].split(",")

    mlst_flag = True
    mlst_profile = list()
    for item in expected_genes:
        for gene in genes:
            if gene.startswith(item):
                mlst_profile.append(gene)

    if len(mlst_profile) < len(expected_genes):
        mlst_flag = False

    if mlst_flag:
        with open("/opt/LPF_databases/mlst_db/mlst_tables/{}.tsv".format(species), 'r') as infile:
            for line in infile:
                if line.startswith("ST"):
                    line = line.rstrip().split("\t")
                    gene_list = list()
                    for i in range(1, len(line)-1):
                        gene_list.append(line[i])
                else:
                    test_set = set()
                    line = line.rstrip().split("\t")
                    for i in range(1, len(line)-1):
                        test_set.add(gene_list[i-1] + '_' + line[i])
                    if test_set.issubset(genes):
                        return line[0], expected_genes, mlst_profile
        return 'Unknown ST', expected_genes, mlst_profile

    return 'Unknown ST', expected_genes, ''


