"""
Shared functions used by the MOSS back-end
"""
import sys
import os
import geocoder
import subprocess
import sqlite3
import json
import datetime
import hashlib
import pandas as pd
from tabulate import tabulate
from fpdf import FPDF
from geopy.geocoders import Nominatim
import matplotlib
import matplotlib.pyplot as plt
from Bio import Phylo
from io import StringIO
import dataframe_image as dfi

def clean_sql_for_moss_run(input_dict):
    pass

def update_sql_database():
    pass

def evaluate_moss_run():
    pass

def validate_date_text(date_text):
    """Validates the date time format"""
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD.")


def validate_input(input_dict):
    """
    {
      "input_file": "file.fastq.gz",
      "input_path": "/opt/moss_data/test_dir/file.fastq.gz",
      "sequencing_method": "nanopore minion",
      "isolation_source": "isolate",
      "investigation_type": "type1",
      "collection_date": "1999-01-19",
      "city": "Copenhagen",
      "country": "Denmark",
      "patient_gender": "",
      "patient_age": "",
      "type_of_infection": "",
      "experimental_condition": "",
      "config_path": "/opt/moss_db/test/"
    }
    """
    print ('Validating input')
    if not input_dict['input_file'] in input_dict['input_path']:
        raise SystemExit('Input file does not match the input path.')
    if not input_dict['input_path'].endswith('.fastq.gz'):
        raise SystemExit('Input is not a fastq.gz file. Only this format is supported.')
    if not input_dict['config_path'].startswith('/opt/moss_db'):
        raise SystemExit('An invalid config_path was given.')
    validate_date_text(input_dict['collection_date'])
    print ('Validation complete')

def parse_finders(input_dict):
    input_dict['resfinder_hits'] = parse_kma_res("{}/finders/resfinder.res".format(input_dict['target_dir']))
    input_dict['virulence_hits'] = parse_kma_res("{}/finders/virulencefinder.res".format(input_dict['target_dir']))
    input_dict['plasmid_hits'] = parse_kma_res("{}/finders/plasmidfinder.res".format(input_dict['target_dir']))
    input_dict['mlst_type'] = parse_mlst_result("{}/mlstresults/data.json".format(input_dict['target_dir']))
    return input_dict

def moss_run(input_dict):
    """
    input_dict = {
        'sample_name': 'file',
        'sequencing_method': 'nanopore minion',
        'isolation_source': 'isolate',
        'investigation_type': 'type1',
        'collection_date': '06-21-1998',
        'input_path': '',
        'city': 'Copenhagen',
        'country': 'Denmark',
        'patient_gender': '',
        'patient_age': '',
        'type_of_infection': '',
        'experimental_condition': '',
        'config_path': '',
        'entry_id': '',
        'moss_db: '',
        'ref_db': '',
        'target_dir': ''
    }
    """

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\"," \
              " type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\"," \
              " time_stamp=\"{}\" WHERE entry_id=\"{}\""\
        .format("CGE finders", input_dict['sample_name'], "Not Determined", "2", "10", "Running",
                str(datetime.datetime.now())[0:-7], input_dict['entry_id'])

    sql_execute_command(sql_cmd, input_dict['moss_db'])

    moss_mkfs(input_dict['config_path'], input_dict['entry_id'])

    kma_finders("-ont -md 5", "resfinder", input_dict, "/opt/moss/resfinder_db/all")
    kma_finders("-ont -md 5", "virulencefinder", input_dict, "/opt/moss/virulencefinder_db/all")
    kma_finders("-ont -md 5", "plasmidfinder", input_dict, "/opt/moss/plasmidfinder_db/all")

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\"," \
              " current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\"" \
              " WHERE entry_id=\"{}\"" \
        .format("KMA Mapping", input_dict['sample_name'], "Not Determined", "3", "10", "Running",
                str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    input_dict = kma_mapping(input_dict)

    associated_species = "{} - assembly from ID: {}".format(input_dict['reference_header_text'], input_dict['entry_id'])

    run_mlst(input_dict)

    input_dict = parse_finders(input_dict)

    if input_dict['template_number'] == None:  # None == no template found
        run_assembly(input_dict)
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\"," \
              " final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("IPC check", input_dict['sample_name'], "Alignment", "4", "10", "Running", str(datetime.datetime.now())[0:-7],
                input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    nanopore_alignment(input_dict)

    input_dict['reference_id'] = sql_fetch_one("SELECT entry_id FROM reference_table WHERE reference_header_text = '{}'"
                                 .format(input_dict['reference_header_text']), input_dict['config_path'])[0]

    sql_execute_command("UPDATE sample_table SET reference_id = '{}' WHERE entry_id = '{}'"
                        .format(input_dict['reference_id'], input_dict['entry_id']), input_dict['moss_db'])

    cmd = "cp {0}{1} {2}/consensus_sequences/{1}"\
        .format(input_dict['target_dir'], input_dict['consensus_name'], input_dict['config_path'])
    os.system(cmd)

    sql_execute_command(
        "UPDATE sample_table SET consensus_name = '{}' WHERE entry_id = '{}'"
            .format(input_dict['consensus_name'], input_dict['entry_id']), input_dict['moss_db'])
    input_dict['isolate_list'] = sql_fetch_all("SELECT consensus_name FROM sample_table WHERE reference_id = '{}'"
            .format(input_dict['reference_id']), input_dict['config_path'])

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\"," \
              " final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("CCphylo", input_dict['sample_name'], "Alignment", "5", "10", "Running",
                str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    input_dict = make_phytree_output_folder(input_dict)

    cmd = "/opt/moss/ccphylo/ccphylo dist --input {0}/phytree_output/* --reference \"{1}\" --min_cov 0.01" \
          " --normalization_weight 0 --output {0}/phytree_output/distance_matrix"\
        .format(input_dict['target_dir'], input_dict['reference_header_text'])
    os.system(cmd)

    distance = ThreshholdDistanceCheck("{}/phytree_output/distance_matrix"
                                       .format(input_dict['target_dir']), input_dict)
    print (distance)
    if distance == None:
        print ("NONE HERE") #Work cataches
        associated_species = "{} - assembly from ID: {}".format(input_dict['reference_header_text'], input_dict['entry_id'])
        run_assembly(input_dict)
    elif distance > 300:  # SNP distance
        associated_species = "{} - assembly from ID: {}".format(input_dict['reference_header_text'],
                                                          input_dict['entry_id'])
        run_assembly(input_dict)
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Distance Matrix", input_dict['sample_name'], "Alignment", "6", "10", "Running", str(datetime.datetime.now())[0:-7],
                input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    os.system("/opt/moss/ccphylo/ccphylo tree --input {0}/phytree_output/distance_matrix --output {0}/phytree_output/tree.newick"\
        .format(input_dict['target_dir']))

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Phylo Tree imaging", input_dict['sample_name'], "Alignment", "7", "10", "Running",
                str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    input_dict = create_phylo_tree(input_dict)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Database updating", input_dict['sample_name'], "Alignment", "8", "10", "Running", str(datetime.datetime.now())[0:-7],
                input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF", input_dict['sample_name'], "Alignment", "9", "10", "Running", str(datetime.datetime.now())[0:-7],
                input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])

    compileReportAlignment(input_dict)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Completed", input_dict['sample_name'], "Alignment", "10", "10", "Completed", str(datetime.datetime.now())[0:-7],
                input_dict['entry_id'])
    sql_execute_command(sql_cmd, input_dict['moss_db'])


    #    input_dict = push_finders_data_sql(input_dict) INSERT AFTER

def derive_phenotype_amr(genes, database):
    new_genes = list()
    for item in genes:
        new_genes.append(item.split("_")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/moss/{}/notes.txt".format(database), 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1]].append(line[0])
                else:
                    phenotype[line[1]] = [line[0]]
    csv_data = []
    csv_data.append(("Resistance", "Genes"))
    for item in phenotype:
        csv_data.append((item, ", ".join(phenotype[item])))
    return phenotype, csv_data

def derive_phenotype_virulence(genes, database, target_dir):
    new_genes = list()
    for item in genes:
        new_genes.append(item.split(":")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/moss/{}/notes.txt".format(database), 'r')
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
    print (csv_data)
    return phenotype, csv_data

def push_meta_data_to_sql(metadata_dict, entry_id, config_path):
    sql_cmd = "INSERT INTO metadata_table(entry_id, sample_name, sequencing_method, isolation_source, investigation_type, \
    collection_date, latitude, longitude, city, country) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entry_id, metadata_dict["sample_name"], metadata_dict["sequencing_method"], metadata_dict["isolation_source"], \
                metadata_dict["investigation_type"], metadata_dict["collection_date"], metadata_dict["latitude"], \
                metadata_dict["longitude"], metadata_dict["city"], metadata_dict["country"])
    sql_execute_command(sql_cmd,  input_dict['config_path'])

def push_finders_data_sql(target_dir, config_path, entry_id):
    resfinder_hits = parse_kma_res("{}/finders/resfinder.res".format(target_dir))
    virulence_hits = parse_kma_res("{}/finders/virulencefinder.res".format(target_dir))
    plasmid_hits = parse_kma_res("{}/finders/plasmidfinder.res".format(target_dir))
    mlst_type = parse_mlst_result("{}/mlstresults/data.json".format(target_dir))

    sql_cmd = "UPDATE sample_table SET amr_genes=\"{}\", virulence_genes=\"{}\", plasmids=\"{}\", mlst=\"{}\" WHERE entry_id=\"{}\"" \
        .format(",".join(resfinder_hits).replace("'", "''"), ",".join(virulence_hits).replace("'", "''"), \
                ",".join(plasmid_hits).replace("'", "''"), mlst_type, entry_id)
    sql_execute_command(sql_cmd,  input_dict['config_path'])

    return resfinder_hits, virulence_hits, plasmid_hits, mlst_type

def parse_mlst_result(filename):
    try:
        with open(filename) as json_file:
            data = json.load(json_file)
        sequence_type = data['mlst']['results']['sequence_type']
        return sequence_type
    except:
        return "Unknown"

def parse_kma_res(filename):
    item_list = list()
    infile = open(filename, 'r')
    for line in infile:
        if line[0] != "#":
            line = line.split('\t')
            item_list.append(line[0])
    return item_list

def kma_finders(arguments, output_name, input_dict, database):
    os.system("/opt/moss/kma/kma -i {} -o {}/finders/{} -t_db {} {}".format(input_dict['input_path'], input_dict['target_dir'], output_name, database, arguments))


def derive_finalized_filenames(input_dir):
    """
    Either, directory have barcode01-barocdeX subdirectories. if so:
        Check number of files. If >1, check combined file. If non, create.
    else:
        evaluate.

    """
    directory_type = None

    sub_directories = os.listdir(input_dir)
    if len(sub_directories) > 1:
        dir_list = list()
        file_list = list()
        for item in sub_directories:
            if os.path.isfile(input_dir + item):
                file_list.append(item)
            elif os.path.isdir(input_dir + item):
                dir_list.append(item)
        if len(dir_list) > 0 and len(file_list) == 0:
            pass
            #Only directoriespass
        elif len(file_list) > 0 and len(dir_list) == 0:
            pass
            #Only files

        elif len(file_list) > 0 and len(dir_list) > 0:
            pass
            #Mix
        #CONTINUE

    else:
        #Check if one fastq
        if os.path.isfile(input_dir + sub_directories[0]):
            if sub_directories[0].endswith('.fastq') or sub_directories[0].endswith('.fastq.gz'):
                #Assume that this one, single fastq file is the whole input.
                return (input_dir + sub_directories[0], "single_input_fastq")
            else:
                sys.exit("The input does not appear to be a fastq file")
        elif os.path.isdir(input_dir + sub_directories[0]):
            if sub_directories[0] != "barcode01":
                sys.exit("The input fastq files given in the metadata sheet are not correct. Please see the documentation at <LINK> for the correct input format.")

    print (sub_directories)

    return ["test", "test2"]


def create_directory_from_dict(dict, path):
    for directory in dict:
        os.system("mkdir {}{}".format(path, directory))
        for subdirectory in dict[directory]:
            os.system("mkdir {}{}/{}".format(path, directory, subdirectory))
    return True

def sql_fetch_one(string, config_path):
    conn = sqlite3.connect("{}/moss.db".format(config_path))
    c = conn.cursor()
    c.execute(string)
    data = c.fetchone()
    conn.close()
    return data

def sql_fetch_all(string, config_path):
    conn = sqlite3.connect("{}/moss.db".format(config_path))
    c = conn.cursor()
    c.execute(string)
    data = c.fetchall()
    data = [item for t in data for item in t]
    conn.close()
    return data

def sql_execute_command(command, moss_db):
    conn = sqlite3.connect(moss_db)
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()

def moss_mkfs(config_path, entry_id):
    target_dir = "{}/analysis/{}/".format(config_path, entry_id)
    os.system("mkdir {}".format(target_dir))
    os.system("mkdir {}/finders".format(target_dir))


def moss_init(input_dict):
    input_dict['entry_id'] = md5_of_file(input_dict['input_path'])
    input_dict['sample_name'] = input_dict['input_path'].split("/")[-1][0:-9]
    input_dict['moss_db'] = "{}/moss.db".format(input_dict['config_path'])
    input_dict['ref_db'] = "{}/REFDB.ATG".format(input_dict['config_path'])
    input_dict['target_dir'] = "{}/analysis/{}/".format(input_dict['config_path'], input_dict['entry_id'])

    check_unique_entry_id(input_dict['entry_id'], input_dict['moss_db'])
    print ('input loaded')
    return input_dict

def get_kma_template_number(input_dict):
    with open('{}/REFDB.ATG.name'.format(input_dict['config_path']), 'r') as infile:
        t = 1
        number = 0
        for line in infile:
            if input_dict['reference_header_text'] in line:
                infile.close()
                return t
            t += 1
        infile.close()
        return t

def make_phytree_output_folder(input_dict):
    cmd = "mkdir {}/phytree_output".format(input_dict['target_dir'])
    os.system(cmd)

    for item in input_dict['isolate_list']: #Can we put this into an sql table too?
        path = "{}/consensus_sequences/{}".format(input_dict['config_path'], item)
        cmd = "cp {} {}/phytree_output/.".format(path, input_dict['target_dir'])
        os.system(cmd)

    input_dict['header_name'] = input_dict['reference_header_text'].split()[0] + '.fsa'
    cmd = "/opt/moss/kma/kma seq2fasta -t_db {} -seqs {} > {}/phytree_output/{}"\
        .format(input_dict['ref_db'], input_dict['template_number'], input_dict['target_dir'], input_dict['header_name'])
    os.system(cmd)

    cmd = "cp {0}*_consensus.fsa {0}phytree_output/.".format(input_dict['target_dir'])
    os.system(cmd)

    return input_dict

def create_phylo_tree(input_dict):
    with open ("{}phytree_output/tree.newick".format(input_dict['target_dir'])) as fd:
        data = fd.read()
    handle = StringIO(data)
    tree = Phylo.read(handle, "newick")
    matplotlib.rc('font', size=20)
    fig = plt.figure(figsize=(20, 20), dpi=80)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes, do_show=False)
    plt.savefig("{}/phytree_output/tree.png".format(input_dict['target_dir']), dpi=100)
    input_dict['phytree_path'] = "{}/phytree_output/tree.png".format(input_dict['target_dir'])
    return input_dict

def plot_tree(treedata, output_file):
    handle = StringIO(treedata)  # parse the newick string
    tree = Phylo.read(handle, "newick")
    matplotlib.rc('font', size=6)
    # set the size of the figure
    fig = plt.figure(figsize=(15, 15), dpi=100)
    # alternatively
    # fig.set_size_inches(10, 20)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes)
    plt.savefig(output_file, dpi=100)

    return

def init_insert_reference_table(config_path):
    infile = open(config_path + "REFDB.ATG.name", 'r')
    t = 1
    conn = sqlite3.connect(config_path + 'moss.db')
    c = conn.cursor()
    ids = list()
    for line in infile:
        line = line.rstrip()
        cmd = "/opt/moss/kma/kma seq2fasta -t_db {}/REFDB.ATG -seqs {}".format(config_path, t)
        proc = subprocess.Popen(cmd, shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0].decode()
        reference_header_text = output.split("\n")[0][1:]
        sequence = output.split("\n")[1]
        entry_id = md5_of_sequence(sequence) #ID for references based on reference sequence
        if entry_id not in ids:
            dbstring = "INSERT INTO reference_table(entry_id, reference_header_text) VALUES('{}', '{}')".format(entry_id, reference_header_text.replace("'", "''"))
            ids.append(entry_id)
            c.execute(dbstring)

        t += 1
    conn.commit()
    conn.close()

def check_assembly_result(path):

    return True

def run_assembly(input_dict):
    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Flye Assembly", "Assembly", "4", "5", "Running", str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd,  input_dict['moss_db'])
    flye_assembly(input_dict)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF report", "Assembly", "5", "5", "Running", str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd,  input_dict['moss_db'])

    compileReportAssembly(input_dict)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Completed", "reference", "5", "5", "Completed", str(datetime.datetime.now())[0:-7], input_dict['entry_id'])
    sql_execute_command(sql_cmd,  input_dict['moss_db'])
    sys.exit("No template was found, so input was added to references.")

def init_moss_variables(config_path, ):
    referenceSyncFile = config_path + "syncFiles/referenceSync.json"
    isolateSyncFile = config_path + "syncFiles/isolateSync.json"
    return "/opt/moss/kma/kma"

def update_pip_dependencies():
    cmd = "python3 -m pip install --upgrade fpdf"
    os.system(cmd)
    cmd = "python3 -m pip install --upgrade tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    pip_list = ["geocoder", "pandas", "geopy", "Nominatim"]
    for item in pip_list:
        cmd = "pip install --upgrade {}".format(item)
        os.system(cmd)

def update_moss_dependencies(laptop, update_list, force):
    if force:
        if laptop:
            print ("laptop FORCE TBD")
        else:
            cmd = "cd /opt/moss/"
            os.system(cmd)
            cmd = "rm -rf kma; rm -rf ccphylo; rm -rf mlst; rm -rf resfinder; rm -rf plasmidfinder; rm -rf virulencefinder;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder.git; cd resfinder; git checkout nanopore_flag; git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git db_resfinder; cd db_resfinder; git checkout minimizer_implementation; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git db_pointfinder; cd db_pointfinder; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/plasmidfinder.git; cd plasmidfinder; git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git; cd plasmidfinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "git clone https://bitbucket.org/genomicepidemiology/virulencefinder.git; cd virulencefinder; git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git; cd virulencefinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
            os.system(cmd)
            cmd = "apt-get install r-base"
            os.system(cmd)
            cmd = "apt install nodejs"
            os.system(cmd)
            cmd = "apt install npm"
            os.system(cmd)
            cmd = "apt install python3-pip"
            os.system(cmd)
            cmd = "apt install docker.io;  systemctl enable --now docker;  usermod -a -G docker $USER;"
            os.system(cmd)

    else:
        if laptop:
            print ("laptop SOFT TBD")
        else:
            if "kma" in update_list:
                cmd = "cd /opt/moss/"
                os.system(cmd)
                cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
                os.system(cmd)
            if "ccphylo" in update_list:
                cmd = "cd /opt/moss/"
                os.system(cmd)
                cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
                os.system(cmd)
            if "docker" in update_list:
                print ("Please make a manual installation of Docker and then run the python docker_images.py script")
            if "r" in update_list:
                cmd = " apt-get install r-base"
                os.system(cmd)
            if "npm" in update_list:
                cmd = " apt install npm"
                os.system(cmd)
            if "python3-pip" in update_list:
                cmd = " apt install python3-pip"
                os.system(cmd)
            if "conda" in update_list:
                print ("Please download conda manually for a full installation!")
    update_pip_dependencies()

def varify_tool(cmd, expected, index_start, index_end):
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode()
    version = output[index_start:index_end]
    print ("{} => {}".format(cmd, version))
    if version >= expected:
        return True
    else:
        return False

def varify_all_dependencies(laptop):
    update_list = []
    if not varify_tool("/opt/moss/kma/kma -v", '1.3.24', -8, -2):#KMA, expected: KMA-1.3.24+
        update_list.append("kma")
    if not varify_tool("/opt/moss/ccphylo/ccphylo -v", '0.5.3', -6, -1): #ccphylo, expected: CCPhylo-0.5.3
        update_list.append("ccphylo")
    if not varify_tool("docker -v", '20.10.8', 15, 22): #docker, Docker version 20.10.8, build 3967b7d28e
        update_list.append("docker")
    if not laptop:
        pass #Test CUDA
        #ont-guppy test
    if not varify_tool("R --version", '4.0.0', 10, 15): #R
        update_list.append("r")
    if not varify_tool("npm -v", '7.0.0', 0, -1): #npm 7.21.1
        update_list.append("npm")
    if not varify_tool("pip --version", '21.0.0', 4, 10): #pip, pip 21.3.1 from /user/etc/etc
        update_list.append("python3-pip")
    if not varify_tool("conda --version", '4.0.0', 6, -1): #conda, conda 4.10.1
        update_list.append("conda")
    return update_list

def run_mlst(input_dict):

    specie = input_dict['reference_header_text'].split()[1].lower() + " " + input_dict['reference_header_text'].split()[2].lower() #Make broader implementation here - fx "ecoli" is for e.coli mlst - how does that worK?

    mlst_dict = dict()

    with open("/opt/moss/mlst/mlst_db/config", 'r') as infile:
        for line in infile:
            if line[0] != "#":
                line = line.split("\t")
                mlst_dict[line[1].lower()] = line[0]

    if specie == "escherichia coli":
        mlst_dict['escherichia coli'] = 'ecoli'


    if specie in mlst_dict:
        cmd = "mkdir {}/mlstresults".format(input_dict['target_dir'])
        os.system(cmd)
        cmd = "python3 /opt/moss/mlst/mlst.py -i {} -o {}mlstresults" \
              " -mp /opt/moss/kma/kma -p /opt/moss/mlst/mlst_db/ -s {} -nano"\
            .format(input_dict['input_path'], input_dict['target_dir'], mlst_dict[specie])
        os.system(cmd)
        input_dict['mlst'] = specie

def sql_string_metadata(metadict):
    entries = ""
    values = ""
    for item in metadict:
        entries += item + ","
        values += "'{}',".format(metadict[item])
    entries = entries[:-1]
    values = values[:-1]
    return entries.replace("'", "''"), values

def prod_metadata_dict(metadata, metadata_headers):
    metadict = dict()
    if '\ufeff' in metadata:
        metadata = metadata.replace(u'\ufeff','').split(",")
    else:
        metadata = metadata.split(",")
    if '\ufeff' in metadata_headers:
        metadata_headers = metadata_headers.replace(u'\ufeff', '').split(",")
    else:
        metadata_headers = metadata_headers.split(",")
    for i in range(len(metadata_headers)):
        metadict[metadata_headers[i]] = metadata[i]
    return metadict

def correctPathCheck(pathName):
    if pathName == "":
        pass
    elif pathName[-1] == "/":
        pass
    else:
        pathName = pathName + "/"
    return pathName

def calc_coordinates_from_location(city, country):
    try:
        geolocator = Nominatim(user_agent="moss")
        loc = geolocator.geocode("{},{}".format(city, country))
        latitude = loc.latitude
        longitude = loc.longitude
    except:
        latitude = ""
        longitude = ""
    return latitude, longitude

def check_coordinates(coordinates):
    try:
        coordinates = geocoder.ip('me').latlng
        geolocator = Nominatim(user_agent="moss")
        location = geolocator.reverse(coordinates)
    except:
        coordinates = ""
        location = ""
    return coordinates, location

def check_alignment_kma_cov(file):
    infile = open(file, 'r')
    top_score = 0
    coverage = 0
    for line in infile:
        if line[0] != "#":
            line = line.rstrip()
            line = line.split("\t")
            if float(line[1]) > top_score:
                top_score = float(line[1])
                coverage = float(line[5])
    infile.close()

    return coverage

def kma_mapping(input_dict):
    os.system("/opt/moss/kma/kma -i {} -o {}kma_mapping -t_db {}/REFDB.ATG"
              " -ID 0 -nf -mem_mode -sasm -ef -1t1".format(input_dict['input_path'], input_dict['target_dir'], input_dict['config_path']))
    num_lines = sum(1 for line in open("{}kma_mapping.res".format(input_dict['target_dir']))) #1 line is empty, more have hits.
    template_score = 0
    if num_lines > 1:
        input_dict['reference_header_text'] = None
        with open("{}kma_mapping.res".format(input_dict['target_dir'])) as infile:
            for line in infile:
                line = line.rstrip()
                line = line.split("\t")
                if line[0][0] != "#":
                    if float(line[1]) > template_score:
                        template_score = float(line[1])
                        input_dict['reference_header_text'] = line[0]
        template_number = findTemplateNumber(input_dict['config_path'], input_dict['reference_header_text'])
        input_dict['template_number'] = template_number
        input_dict['reference_header_text'] = input_dict['reference_header_text']
        if " " in input_dict['reference_header_text']:
            input_dict['accesion'] = input_dict['reference_header_text'].split(" ")[0]
        else:
            input_dict['accesion'] = input_dict['reference_header_text']
        input_dict['consensus_name'] = "{}_{}_consensus.fsa".format(input_dict['sample_name'], input_dict['accesion'])

        return input_dict
    else:
        print("None of the given templates matches any of the entries in given ref_kma_database."
              " The input reads will now be assembled and added to the reference ref_kma_database as a new reference.")
        input_dict['template_number'] = None
        input_dict['reference_header_text'] = None
        return input_dict

def nanopore_alignment(input_dict):
    cmd = "/opt/moss/kma/kma -i {} -o {}{} -t_db {}/REFDB.ATG -mint3 -Mt1 {} -t 8"\
        .format(input_dict['input_path'], input_dict['target_dir'], input_dict['consensus_name'][:-4],
                input_dict['config_path'], str(input_dict['template_number']))
    os.system(cmd)

def concatenateDraftGenome(input_file):
    cmd = "grep -c \">\" {}".format(input_file)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = int(output.decode().rstrip())
    input_name = input_file.split("/")[-1]
    new_name = ""
    if id > 1:
        input_path = "/".join(input_file.split("/")[:-1])
        new_name = input_path + "concatenated_" + input_name
        infile = open(input_file, 'r')
        writefile = open(new_name, 'w')
        sequence = ""
        for line in infile:
            if line[0] != ">":
                line = line.rstrip()
                sequence += line
        print(">concatenated_" + input_name, file=writefile)
        print(sequence, file=writefile)
        infile.close()
        writefile.close()
    return id, new_name

def sequence_from_fasta_file(file_path):
    sequence = ''
    with open(file_path, 'r') as fd:
        for line in fd:
            if not line.startswith(">"):
                line = line.rstrip()
                sequence += line
    return sequence

def md5_of_sequence(sequence):
    hash_md5 = hashlib.md5(sequence.encode())
    return hash_md5.hexdigest()

def md5_of_file(file_path):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        lines = f.read()
        m.update(lines)
    md5code = m.hexdigest()
    return md5code


def ThreshholdDistanceCheck(distancematrixfile, input_dict):
    infile = open(distancematrixfile, 'r')
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == input_dict['consensus_name'] or line[0] == input_dict['header_name']:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == input_dict['consensus_name'] or line[0] == input_dict['header_name']:
                index = linecount
                secondentry = True
        linecount += 1
    return None

def flye_assembly(input_dict):
    print ("Made it to flye")
    cmd = "docker run --name assembly_{0} -v {1}:/tmp/{2} staphb/flye flye -o /tmp/assembly_results" \
          " --threads 8 --nano-raw /tmp/{2}"\
        .format(input_dict['entry_id'], input_dict['input_path'], input_dict['input_file'])
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_", input_dict['entry_id']), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/assembly_results {}.".format(id, input_dict['target_dir'])
    os.system(cmd)
    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    # Concatenate contigs
    with open("{}assembly_results/assembly.fasta".format(input_dict['target_dir']), 'r') as infile:
        with open("{}{}_assembly.fasta".format(input_dict['target_dir'], input_dict['sample_name']), 'w') as outfile:
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line

            if input_dict['reference_header_text'].startswith(">Assembly"):
                new_header_text = ">{}_Assembly_{}".format(input_dict['reference_id'], input_dict['reference_header_text'][1:]
                                                           .split("_Assembly_")[-1])
            else:
                new_header_text = ">{}_Assembly_{}".format(input_dict['reference_id'], input_dict['reference_header_text'][1:])
            print(new_header_text, file=outfile)
            print(sequence, file=outfile)

    os.system("/opt/moss/kma/kma index -t_db {} -i {}{}_assembly.fasta"\
        .format(input_dict['ref_db'], input_dict['target_dir'], input_dict['sample_name']))

    #c = conn.cursor()
    #dbstring = "INSERT INTO reference_table(entry_id, input_dict['reference_header_text']) VALUES('{}', '{}')".format(entry_id, new_header_text[1:])
    #c.execute(dbstring)
    #conn.commit()
    #conn.close()

def check_unique_entry_id(entry_id, moss_db):

    conn = sqlite3.connect(moss_db)
    c = conn.cursor()

    c.execute("SELECT * FROM sample_table WHERE entry_id = '{}'".format(entry_id))
    refdata = c.fetchall()

    if refdata != []:
        sys.exit('An isolate sample has the same filename as your input.'
                 ' Your input is likely a duplicate which has already been analyzed.')

    conn.close()

def findTemplateNumber(config_path, name):
    if name == None:
        return ""
    infile = open("{}/REFDB.ATG.name".format(config_path), 'r')
    t = 1
    for line in infile:
        if line.rstrip() == name:
            infile.close()
            return t
        else:
            t = t + 1
    infile.close()

def run_quast(target_dir, jobid):
    cmd = "docker run --name quast{} -v {}/assembly_results/:/data/assembly_results/ staphb/quast quast.py /data/assembly_results/assembly.fasta -o /output/quast_output".format(
        jobid, target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("quast", jobid), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/output/quast_output {}quast_output".format(id, target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)

def isolate_file_name(config_path, entry_id):
    isolatedb = "{}/moss.db".format(config_path)
    conn = sqlite3.connect(isolatedb)
    c = conn.cursor()

    c.execute("SELECT sample_name FROM sample_table WHERE entry_id = '{}'".format(entry_id))
    refdata = c.fetchall()
    conn.close()
    element = refdata[0][0]

    return element

def run_bandage(target_dir, jobid):
    #TBD run bandage in assembly func
    cmd = "docker run --name bandage{} -v {}/assembly_results/:/data/assembly_results/ nanozoo/bandage Bandage image /data/assembly_results/assembly_graph.gfa contigs.jpg".format(
        jobid, target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("bandage", jobid), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:contigs.jpg {}contigs.jpg".format(id, target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)

def compileReportAssembly(input_dict):
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(input_dict['entry_id'])

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, input_dict['entry_id'], "MOSS analytical report")
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "Suggested reference: {} \n\n" \
                 "No related phylogeny cluster was identified. \n" \
                 "".format(input_dict['entry_id'], input_dict['associated_species']) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(20)

    run_quast(input_dict['target_dir'], input_dict['entry_id'])

    df = pd.read_csv(input_dict['target_dir'] + "quast_output/report.tsv", sep='\t')

    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    dfi.export(df_styled, input_dict['target_dir'] + "quast_table.png")
    pdf.image("{}quast_table.png".format(input_dict['target_dir']), x=10, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)
    run_bandage(input_dict['target_dir'], ID)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.image("{}contigs.jpg".format(input_dict['target_dir']), x=115, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, input_dict['entry_id'], "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    amr_pheno, csv_data = derive_phenotype_amr(input_dict['resfinder_hits'], "resfinder_db")

    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    for row in csv_data:
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1,
                           new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    virulence_pheno, csv_data = derive_phenotype_virulence(input_dict['virulence_hits'],
                                                           "virulencefinder_db", input_dict['target_dir'])
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    for row in csv_data:
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1,
                           new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in input_dict['plasmid_hits']:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.set_font('Arial', '', 12)

    pdf.output(input_dict['target_dir'] + filename, 'F')

def mlst_sequence_type(target_dir):
    try:
        with open(target_dir + "mlstresults/data.json") as json_file:
            data = json.load(json_file)
        sequence_type = data['mlst']['results']['sequence_type']
        return sequence_type
    except:
        return "No MLST Found"

def compileReportAlignment(input_dict):
    pdf = FPDF()  # A4 (210 by 297 mm)

    filename = "{}_report.pdf".format(input_dict['entry_id']) #ADD idd
    clusterSize = len(input_dict['isolate_list'])

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)

    create_title(pdf, input_dict['entry_id'], "MOSS analytical report")
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)

    textstring = "ID: {} \n" \
                 "sample_name: {} \n" \
                 "Identified reference: {} \n" \
                 "".format(input_dict['entry_id'], input_dict['sample_name'], input_dict['reference_header_text'])
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)

    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 153, 255)
    pdf.set_xy(x=10, y=60)
    pdf.cell(85, 5, "Sample information: ", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)

    pdf.set_font('Arial', '', 10)
    textstring = "Copenhagen, Denmark \n" \
                 "Time of sampling: 2019-06-11 18:03:00. \n" \
                 "Number of associated isolates: {} \n" \
                 "".format(clusterSize)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)
    pdf.set_text_color(51, 153, 255)
    pdf.set_font('Arial', '', 12)
    pdf.cell(85, 5, "CGE results: ", 0, 1, 'L')

    textstring = "AMR genes in this sample: {}. \n" \
                 "Plasmids in this sample: {}. \n" \
                 "Virulence genes in this sample: {}. \n" \
                 "MLST: ST{}. \n" \
                 "".format(len(input_dict['resfinder_hits']), len(input_dict['plasmid_hits']), len(input_dict['virulence_hits']), input_dict['mlst_type'])
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, input_dict['entry_id'], "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    amr_pheno, csv_data = derive_phenotype_amr(input_dict['resfinder_hits'], "resfinder_db")
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    for row in csv_data:
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1,
                           new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    virulence_pheno, csv_data = derive_phenotype_virulence(input_dict['virulence_hits'], "virulencefinder_db", input_dict['target_dir'])
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    for row in csv_data:
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1,
                           new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in input_dict['plasmid_hits']:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.set_font('Arial', '', 12)

    ''' Third Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, input_dict['entry_id'], "Cluster phylogeny:")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Phylo tree for cluser {}: ".format(input_dict['reference_header_text'].split("\t")[0]), 0, 1, 'L')

    input_dict = create_phylo_tree(input_dict)

    pdf.image("{}/phytree_output/tree.png".format(input_dict['target_dir']), x=10, y=55, w=pdf.w / 1.5, h=pdf.h / 1.75)

    pdf.output(input_dict['target_dir'] + filename, 'F')

def resfinderPage(tabfile, pdf, target_dir):
    infile = open(tabfile, 'r')
    t = 0
    data = []
    for line in infile:
        line = line.rstrip().split("\t")
        if t == 0:
            line[2] = "Gene Length"
        else:
            if line[7] == "Warning: gene is missing from Notes file. Please inform curator.":
                line[7] = "NA."
        data.append(line)
        t += 1
    infile.close()
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "ResFinder Profile:")
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 7)
    table = tabulate(data, headers='firstrow', tablefmt='plain')
    pdf.write(5, f"{table}")

def virulencePage(jsoninput, pdf, target_dir):
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "VirulenceFinder Profile:")
    pdf.ln(10)
    with open(jsoninput) as json_file:
        data = json.load(json_file)
    for species in data['virulencefinder']['results']:
        pdf.set_font('Arial', 'B', 14)
        pdf.write(5, f"{species}")
        pdf.ln(5)
        for hit in data['virulencefinder']['results'][species]:
            pdf.set_font('Arial', 'B', 8)
            if type(data['virulencefinder']['results'][species][hit]) == dict:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.ln(5)
                for gene in data['virulencefinder']['results'][species][hit]:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.write(5, f"{gene}")
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 8)
                    for info in data['virulencefinder']['results'][species][hit][gene]:
                        string = "       {} : {}".format(info, data['virulencefinder']['results'][species][hit][gene][info])
                        pdf.write(5, f"{string}")
                        pdf.ln(5)
                    pdf.ln(10)
            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 8)
                pdf.write(5, f"{data['virulencefinder']['results'][species][hit]}")
                pdf.ln(10)

def plasmid_data_for_report(jsoninput, target_dir):
    if os.path.isfile(jsoninput):
        with open(jsoninput) as json_file:
            data = json.load(json_file)
        count1 = 0
        plasmid_list = []
        for species in data['plasmidfinder']['results']:
            for hit in data['plasmidfinder']['results'][species]:
                if type(data['plasmidfinder']['results'][species][hit]) == dict:
                    print (data['plasmidfinder']['results'][species][hit])
                    for gene in data['plasmidfinder']['results'][species][hit]:
                        count1 += 1
                        plasmid_list.append(gene)
    else:
        count1 = 0
        plasmid_list = []
    return count1, plasmid_list

def virulence_data_for_report(jsoninput, target_dir):
    #HERE SOMETHINIG HAPPEND CHECK
    if os.path.isfile(jsoninput):
        with open(jsoninput) as json_file:
            data = json.load(json_file)
        count1 = 0

        virulence_list = []
        for species in data['virulencefinder']['results']:

            for hit in data['virulencefinder']['results'][species]:
                if type(data['virulencefinder']['results'][species][hit]) == dict:
                    print (data['virulencefinder']['results'][species][hit])

                    for gene in data['virulencefinder']['results'][species][hit]:
                        count1 += 1
                        virulence_list.append(gene)
    else:
        count1 = 0
        virulence_list = []

    return count1, virulence_list

def plasmidPage(jsoninput, pdf, target_dir):
    pdf.set_font('Arial', 'B', 24)
    pdf.write(5, "PlasmidFinder Profile:")
    pdf.ln(10)
    with open(jsoninput) as json_file:
        data = json.load(json_file)
    for species in data['plasmidfinder']['results']:
        pdf.set_font('Arial', 'B', 14)
        pdf.write(5, f"{species}")
        pdf.ln(5)
        for hit in data['plasmidfinder']['results'][species]:
            pdf.set_font('Arial', 'B', 8)
            if type(data['plasmidfinder']['results'][species][hit]) == dict:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.ln(5)
                for gene in data['plasmidfinder']['results'][species][hit]:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.write(5, f"{gene}")
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 8)
                    for info in data['plasmidfinder']['results'][species][hit][gene]:
                        string = "       {} : {}".format(info, data['plasmidfinder']['results'][species][hit][gene][info])
                        pdf.write(5, f"{string}")
                        pdf.ln(5)
                    pdf.ln(10)
            else:
                pdf.set_font('Arial', 'B', 12)
                pdf.write(5, f"{hit}")
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 8)
                pdf.write(5, f"{data['plasmidfinder']['results'][species][hit]}")
                pdf.ln(10)

def create_title(pdf, id, string):
  # Unicode is not yet supported in the py3k version; use windows-1252 standard font
  pdf.set_text_color(51, 153, 255)
  pdf.set_font('Arial', 'BU', 36)
  pdf.ln(10)
  pdf.write(5, f"{string}")
  pdf.ln(10)
  pdf.set_text_color(0, 0, 0)