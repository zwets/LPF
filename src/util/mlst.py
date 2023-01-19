import sys
def derive_mlst_species(reference_header_text):
    specie = reference_header_text.split()[1].lower() + " " + reference_header_text.split()[2].lower()
    mlst_dict = dict()
    if specie == "escherichia coli":  # special
        return 'ecoli'
    else:
        with open("/opt/moss_databases/mlst_db/config", 'r') as infile:
            for line in infile:
                if line[0] != "#":
                    line = line.split("\t")
                    mlst_dict[line[1].lower()] = line[0]
    if specie in mlst_dict or specie == 'ecoli':
        return specie
    else:
        return 'Unknown'

def determine_mlst(bacterial_parser):
    """Returns the mlst results"""
    with open("/opt/moss_databases/mlst_db/config", 'r') as fd:
        for line in fd:
            if line[0] != "#":
                line = line.rstrip().split("\t")
                if line[0] == bacterial_parser.mlst_species:
                    expected_genes = line[2].split(",")

    if expected_genes == None: #No MLST database for this specie
        return None

    found_genes = dict()
    with open(bacterial_parser.target_dir + '/finders/mlst_mapping.res', 'r') as infile:
        for line in infile:
            if line[0] == "#":
                line = line.rstrip().split("\t")
                gene = line[0].split("_")[0]
                number = line[0].split("_")[-1]
                if gene in expected_genes:
                    found_genes[gene] = number

    if len(found_genes) == len(expected_genes): #All genes found for mlst
        with open("/opt/moss_databases/mlst_db/mlst_talbes/{}.tsv".format(bacterial_parser.mlst_species), 'r'):
            for line in infile:
                if line.startswith("ST"):
                    line = line.rstrip().split("\t")
                    current_scheme = dict()
                    for i in range(1, len(line)-1):
                        current_scheme[line[i]] = 0
                    sys.exit('Found scheme: {}'.format(current_scheme))


