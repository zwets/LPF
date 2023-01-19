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
        if gene in found_genes:
            if gene.startswith(item):
                pass
        else:
            mlst_flag = False

    if mlst_flag:
        print ("All MLST genes found")
    else:
        print ("Not all MLST genes found")

    print (found_genes)

    if len(found_genes) == len(expected_genes): #All genes found for mlst
        with open("/opt/moss_databases/mlst_db/mlst_talbes/{}.tsv".format(bacterial_parser.data.mlst_species), 'r'):
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
                        test_set.add(gene_list[i] + line[i])
                    print (test_set)

    else:
        return 'Unknown'

