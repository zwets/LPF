import sys
import logging
def derive_mlst_species(reference_header_text):
    specie = reference_header_text.split(' ')[1] + ' ' + reference_header_text.split(' ')[2]
    mlst_species = reference_header_text.split(' ')[1][0].lower() + reference_header_text.split(' ')[2].lower()
    print (specie, mlst_species)
    mlst_dict = dict()
    if specie == "mlst_species":  # special
        return specie, 'ecoli'
    else:
        with open("/opt/LPF_databases/mlst_db/config", 'r') as infile:
            for line in infile:
                if line[0] != "#":
                    line = line.split("\t")
                    mlst_dict[line[1].lower()] = line[0]
    if mlst_species in mlst_dict or mlst_species == 'ecoli':
        return specie, mlst_species
    else:
        return specie, 'No MLST Scheme'

def determine_mlst(bacterial_parser):
    """Returns the mlst results"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    with open("/opt/LPF_databases/mlst_db/config", 'r') as fd:
        for line in fd:
            if line[0] != "#":
                line = line.rstrip().split("\t")
                if line[0] == bacterial_parser.data.mlst_species:
                    expected_genes = line[2].split(",")
    print (expected_genes)

    if expected_genes == None: #No MLST database for this specie
        return None

    found_genes = set()
    with open(bacterial_parser.data.target_dir + '/finders/mlst_mapping.res', 'r') as infile:
        for line in infile:
            if line[0] != "#":
                line = line.rstrip().split("\t")
                gene = line[0].split("_")[0]
                if gene in expected_genes:
                    found_genes.add(line[0])

    mlst_flag = True
    for item in expected_genes:
        for gene in found_genes:
            if gene.startswith(item):
                break
        else:
            mlst_flag = False

    if mlst_flag:
        with open("/opt/LPF_databases/mlst_db/mlst_tables/{}.tsv".format(bacterial_parser.data.mlst_species), 'r') as infile:
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
                    if test_set.issubset(found_genes):
                        bacterial_parser.logger.info("MLST: {}".format(line[0]))
                        return line[0]
    logger.info("No MLST found")
    return 'Unknown'
