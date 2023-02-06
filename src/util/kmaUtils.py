import os

def findTemplateNumber(name, database):
    if os.path.exists(database + ".name"):
        with open(database + ".name") as f:
            t = 1
            for line in f:
                if line.rstrip() == name:
                    return t
                else:
                    t += 1
                    
def parse_finders(bacterial_parser):
    bacterial_parser.data.resfinder_hits = parse_kma_res("{}/finders/resfinder.res".format(bacterial_parser.data.target_dir))
    bacterial_parser.data.virulence_hits = parse_kma_res("{}/finders/virulencefinder.res".format(bacterial_parser.data.target_dir))
    bacterial_parser.data.plasmid_hits = parse_kma_res("{}/finders/plasmidfinder.res".format(bacterial_parser.data.target_dir))

def parse_kma_res(filename):
    item_list = list()
    infile = open(filename, 'r')
    for line in infile:
        if line[0] != "#":
            line = line.split('\t')
            item_list.append(line[0])
    return item_list