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