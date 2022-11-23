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
import logging

#import src.moss_helpers as moss_helpers
#from .version import __version__

def moss_run(moss_object):
    #moss_helpers.begin_logging(moss_object.target_dir + moss_object.entry_id + '.log')
    #try:
    #    pass
    #except Exception as e:
    #    logging.error(e, exc_info=True)
    #    raise

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\"," \
              " type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\"," \
              " time_stamp=\"{}\" WHERE entry_id=\"{}\""\
        .format("CGE finders", moss_object.sample_name, "Not Determined", "2", "10", "Running",
                str(datetime.datetime.now())[0:-7], moss_object.entry_id)

    sql_execute_command(sql_cmd, moss_object.moss_db)

    moss_mkfs(moss_object.config_path, moss_object.entry_id)

    kma_finders("-ont -md 5", "resfinder", moss_object, "/opt/moss/resfinder_db/all")
    kma_finders("-ont -md 5", "virulencefinder", moss_object, "/opt/moss/virulencefinder_db/all")
    kma_finders("-ont -md 5", "plasmidfinder", moss_object, "/opt/moss/plasmidfinder_db/all")

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\"," \
              " current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\"" \
              " WHERE entry_id=\"{}\"" \
        .format("KMA Mapping", moss_object.sample_name, "Not Determined", "3", "10", "Running",
                str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    moss_object = kma_mapping(moss_object)

    moss_object.associated_species = "{} - assembly from ID: {}".format(moss_object.reference_header_text, moss_object.entry_id)

    run_mlst(moss_object)

    moss_object = parse_finders(moss_object)

    if moss_object.template_number == None:  # None == no template found
        run_assembly(moss_object)
        return moss_object
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\"," \
              " final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("IPC check", moss_object.sample_name, "Alignment", "4", "10", "Running", str(datetime.datetime.now())[0:-7],
                moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    nanopore_alignment(moss_object)

    moss_object.reference_id = sql_fetch_one("SELECT entry_id FROM reference_table WHERE reference_header_text = '{}'"
                                 .format(moss_object.reference_header_text), moss_object.moss_db)[0]

    cmd = "cp {0}{1} {2}consensus_sequences/{1}"\
        .format(moss_object.target_dir, moss_object.consensus_name, moss_object.config_path)
    os.system(cmd)

    moss_object.isolate_list = sql_fetch_all("SELECT consensus_name FROM sample_table WHERE reference_id = '{}'"
            .format(moss_object.reference_id), moss_object.moss_db) #Not all isolates are used current is not included either.

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\"," \
              " final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("CCphylo", moss_object.sample_name, "Alignment", "5", "10", "Running",
                str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    moss_object = make_phytree_output_folder(moss_object)


    cmd = "~/bin/ccphylo dist --input {0}/phytree_output/* --reference \"{1}\" --min_cov 0.01" \
          " --normalization_weight 0 --output {0}/phytree_output/distance_matrix"\
        .format(moss_object.target_dir, moss_object.reference_header_text)
    os.system(cmd)

    distance = ThreshholdDistanceCheck("{}/phytree_output/distance_matrix"
                                       .format(moss_object.target_dir), moss_object)
    print (distance)
    if distance == None:
        moss_object.associated_species = "{} - assembly from ID: {}".format(moss_object.reference_header_text, moss_object.entry_id)
        run_assembly(moss_object)
        return moss_object
    elif distance > 300:  # SNP distance
        moss_object.associated_species = "{} - assembly from ID: {}".format(moss_object.reference_header_text,
                                                          moss_object.entry_id)
        run_assembly(moss_object)
        return moss_object
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Distance Matrix", moss_object.sample_name, "Alignment", "6", "10", "Running", str(datetime.datetime.now())[0:-7],
                moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    os.system("~/bin/ccphylo tree --input {0}/phytree_output/distance_matrix --output {0}/phytree_output/tree.newick"\
        .format(moss_object.target_dir))

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Phylo Tree imaging", moss_object.sample_name, "Alignment", "7", "10", "Running",
                str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    moss_object = create_phylo_tree(moss_object)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Database updating", moss_object.sample_name, "Alignment", "8", "10", "Running", str(datetime.datetime.now())[0:-7],
                moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF", moss_object.sample_name, "Alignment", "9", "10", "Running", str(datetime.datetime.now())[0:-7],
                moss_object.entry_id)
    sql_execute_command(sql_cmd, moss_object.moss_db)

    compileReportAlignment(moss_object)
    return moss_object


def update_meta_data_table(moss_object):
    attributes = [a for a in dir(moss_object) if not a.startswith('__')]
    for attribute in attributes:
        val = getattr(moss_object, attribute)
        if isinstance(val, list) and len(val) > 0:
            for i in range(len(val)):
                if "'" in val[i]:
                    val[i] = val[i].replace("'", "''")
        else:
            if isinstance(val, str) and "'" in val:
                val = val.replace("'", "''")
        moss_object.attribute = val
    sql_dict = dict()
    for attribute in attributes:
        sql_dict[attribute] = moss_object.attribute()
    print (sql_dict)
    sql_cmd = "INSERT INTO meta_data_table(entry_id, meta_data_json) VALUES('{}', '{}')".format(moss_object.entry_id, json.dumps(sql_dict))
    sql_execute_command(sql_cmd, moss_object.moss_db)

def update_reference_table(moss_object):
    sql_cmd = "INSERT INTO reference_table(entry_id, reference_header_text) VALUES('{}', '{}')".format(moss_object.entry_id, moss_object.reference_header_text)
    sql_execute_command(sql_cmd, moss_object.moss_db)

def update_sample_table(moss_object):
    sql_cmd = "INSERT INTO sample_table(entry_id, sample_name, reference_id, consensus_name) VALUES('{}', '{}', '{}', '{}')".format(moss_object.entry_id, moss_object.sample_name, moss_object.reference_id, moss_object.consensus_name)
    sql_execute_command(sql_cmd, moss_object.moss_db)
    return True
def insert_sql_data_to_db(moss_object, r_type):
    update_sample_table(moss_object)
    update_meta_data_table(moss_object)
    if r_type == 'assembly':
        update_reference_table(moss_object)

    return True

def qc_check(moss_object):
    """Very basic QC. Only checks for a minimum amount of input data so far."""
    file_size_mb = os.path.getsize(moss_object.input_path)/1000000
    if 3 > file_size_mb:
        sys.exit('The input file was less than 3 MB. This likely means only a very small amount of DNA was sequenced. Analysis can not be performed.')
    return True

def create_sql_db(config_name):
    conn = sqlite3.connect(config_name + 'moss.db')
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS sample_table(entry_id TEXT PRIMARY KEY, sample_name TEXT, reference_id TEXT, consensus_name TEXT)""")
    conn.commit()
    c.execute(
        """CREATE TABLE IF NOT EXISTS reference_table(entry_id TEXT PRIMARY KEY, reference_header_text TEXT)""")  # Mangler finder results. Implement eventually
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS meta_data_table(entry_id TEXT PRIMARY KEY, meta_data_json TEXT)""")
    conn.commit()
    c.execute(
        """CREATE TABLE IF NOT EXISTS status_table(entry_id TEXT PRIMARY KEY, sample_name TEXT, status TEXT, type TEXT, current_stage TEXT, final_stage TEXT, result TEXT, time_stamp TEXT)""")
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS sync_table(last_sync TEXT, sync_round TEXT)""")
    conn.commit()
    c.execute(
        """CREATE TABLE IF NOT EXISTS basecalling_table(name TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT)""")
    conn.commit()
    dbstring = "INSERT INTO sync_table(last_sync) VALUES('{}')".format(str(datetime.datetime.now())[0:-7])
    c.execute(dbstring)
    conn.commit()
    conn.close()

    init_insert_reference_table(config_name)

def clean_sql_for_moss_run(moss_object):
    print ('cleaning sql for failed run.')
    sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\"," \
              " type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\"," \
              " time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Run failed", moss_object.sample_name, "Run failed", "0", "0", "Run failed",
                str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    return sql_cmd

def completed_run_update_sql_database(r_type, moss_object):
    if r_type == 'alignment':
        sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
            .format("Completed", moss_object.sample_name, "Alignment", "10", "10", "Completed",
                    str(datetime.datetime.now())[0:-7],
                    moss_object.entry_id)
        sql_execute_command(sql_cmd, moss_object.moss_db)
    elif r_type == 'assembly':
        sql_cmd = "UPDATE status_table SET status=\"{}\", sample_name =\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
            .format("Completed", moss_object.sample_name, "Assembly", "5", "5", "Assembly",
                    str(datetime.datetime.now())[0:-7],
                    moss_object.entry_id)
        sql_execute_command(sql_cmd, moss_object.moss_db)
    else:
        return None

def evaluate_moss_run(moss_object): #TBD. Not implemented yet. Will be used to evaluate if the run finished correctly or if sql should be cleaned.
    if moss_object.reference_id == None:
        return 'assembly'
    else:
        return 'alignment'

def validate_date_text(date_text):
    """Validates the date time format"""
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD.")

def parse_finders(moss_object):
    moss_object.resfinder_hits = parse_kma_res("{}/finders/resfinder.res".format(moss_object.target_dir))
    moss_object.virulence_hits = parse_kma_res("{}/finders/virulencefinder.res".format(moss_object.target_dir))
    moss_object.plasmid_hits = parse_kma_res("{}/finders/plasmidfinder.res".format(moss_object.target_dir))
    moss_object.mlst_type = parse_mlst_result("{}/mlstresults/data.json".format(moss_object.target_dir))
    return moss_object
def derive_amr_stats(genes, database): #TBD rewrite and remove.
    phenotype = dict()
    infile = open("/opt/moss/{}/phenotypes.txt".format(database), 'r')
    for line in infile:
        if not line.startswith("Gene_accession"):
            line = line.rstrip().split("\t")
            if line[0] in genes:
                phenotype[line[0]] = [line[1], line[2]]
    csv_data = []
    csv_data.append(("Gene", "Resistance Class", "Phenotype"))
    for item in phenotype:
        csv_data.append([item, phenotype[item][0], phenotype[item][1]])
    return csv_data

def derive_virulence_stats(genes, database, target_dir):  #TBD rewrite and remove.
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
    return csv_data

def push_finders_data_sql(target_dir, config_path, entry_id): #TBD insert all meta data into sql and the end after a succesfull run.
    resfinder_hits = parse_kma_res("{}/finders/resfinder.res".format(target_dir))
    virulence_hits = parse_kma_res("{}/finders/virulencefinder.res".format(target_dir))
    plasmid_hits = parse_kma_res("{}/finders/plasmidfinder.res".format(target_dir))
    mlst_type = parse_mlst_result("{}/mlstresults/data.json".format(target_dir))

    sql_execute_command(sql_cmd,  moss_object.config_path)

    return resfinder_hits, virulence_hits, plasmid_hits, mlst_type

def parse_mlst_result(filename): #TBD rewrite
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

def kma_finders(arguments, output_name, moss_object, database):
    os.system("~/bin/kma -i {} -o {}/finders/{} -t_db {} {}".format(moss_object.input_path, moss_object.target_dir, output_name, database, arguments))

def create_directory_from_dict(dict, path):
    for directory in dict:
        os.system("mkdir {}{}".format(path, directory))
        for subdirectory in dict[directory]:
            os.system("mkdir {}{}/{}".format(path, directory, subdirectory))
    return True

def sql_fetch_one(string, moss_db):
    conn = sqlite3.connect(moss_db)
    c = conn.cursor()
    c.execute(string)
    data = c.fetchone()
    conn.close()
    return data

def sql_fetch_all(string, moss_db):
    conn = sqlite3.connect(moss_db)
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

def moss_init(moss_object):
    moss_object.entry_id = md5_of_file(moss_object.input_path)
    moss_object.sample_name = moss_object.input_path.split("/")[-1][0:-9]
    moss_object.moss_db = "{}/moss.db".format(moss_object.config_path)
    moss_object.ref_db = "{}/REFDB.ATG".format(moss_object.config_path)
    moss_object.target_dir = "{}/analysis/{}/".format(moss_object.config_path, moss_object.entry_id)
    print ('input loaded')
    return moss_object

def get_kma_template_number(moss_object):
    with open('{}/REFDB.ATG.name'.format(moss_object.config_path), 'r') as infile:
        t = 1
        number = 0
        for line in infile:
            if moss_object.reference_header_text in line:
                infile.close()
                return t
            t += 1
        infile.close()
        return t

def make_phytree_output_folder(moss_object):
    cmd = "mkdir {}/phytree_output".format(moss_object.target_dir)
    os.system(cmd)

    for item in moss_object.isolate_list: #Can we put this into an sql table too?
        path = "{}/consensus_sequences/{}".format(moss_object.config_path, item)
        cmd = "cp {} {}/phytree_output/.".format(path, moss_object.target_dir)
        os.system(cmd)
    os.system("cp {}consensus_sequences/{} {}/phytree_output/.".format(moss_object.config_path, moss_object.consensus_name, moss_object.target_dir))


    moss_object.header_name = moss_object.reference_header_text.split()[0] + '.fsa'
    cmd = "~/bin/kma seq2fasta -t_db {} -seqs {} > {}/phytree_output/{}"\
        .format(moss_object.ref_db, moss_object.template_number, moss_object.target_dir, moss_object.header_name)
    os.system(cmd)

    cmd = "cp {0}*_consensus.fsa {0}phytree_output/.".format(moss_object.target_dir)
    os.system(cmd)

    return moss_object

def create_phylo_tree(moss_object):
    with open ("{}phytree_output/tree.newick".format(moss_object.target_dir)) as fd:
        data = fd.read()
    handle = StringIO(data)
    tree = Phylo.read(handle, "newick")
    matplotlib.rc('font', size=20)
    fig = plt.figure(figsize=(20, 20), dpi=80)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes, do_show=False)
    plt.savefig("{}/phytree_output/tree.png".format(moss_object.target_dir), dpi=100)
    moss_object.phytree_path = "{}/phytree_output/tree.png".format(moss_object.target_dir)
    return moss_object

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
        cmd = "~/bin/kma seq2fasta -t_db {}/REFDB.ATG -seqs {}".format(config_path, t)
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

def run_assembly(moss_object):
    moss_object.reference_id = None
    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Flye Assembly", "Assembly", "4", "5", "Running", str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd,  moss_object.moss_db)
    flye_assembly(moss_object)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\"," \
              " result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Compiling PDF report", "Assembly", "5", "5", "Running", str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd,  moss_object.moss_db)

    compileReportAssembly(moss_object)

    sql_cmd = "UPDATE status_table SET status=\"{}\", type=\"{}\", current_stage=\"{}\", final_stage=\"{}\", result=\"{}\", time_stamp=\"{}\" WHERE entry_id=\"{}\"" \
        .format("Completed", "reference", "5", "5", "Completed", str(datetime.datetime.now())[0:-7], moss_object.entry_id)
    sql_execute_command(sql_cmd,  moss_object.moss_db)

def init_moss_variables(config_path, ):
    referenceSyncFile = config_path + "syncFiles/referenceSync.json"
    isolateSyncFile = config_path + "syncFiles/isolateSync.json"
    return "~/bin/kma"

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
    if not varify_tool("~/bin/kma -v", '1.3.24', -8, -2):#KMA, expected: KMA-1.3.24+
        update_list.append("kma")
    if not varify_tool("~/bin/ccphylo -v", '0.5.3', -6, -1): #ccphylo, expected: CCPhylo-0.5.3
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

def run_mlst(moss_object):

    specie = moss_object.reference_header_text.split()[1].lower() + " " + moss_object.reference_header_text.split()[2].lower() #Make broader implementation here - fx "ecoli" is for e.coli mlst - how does that worK?

    mlst_dict = dict()

    with open("/opt/moss/mlst/mlst_db/config", 'r') as infile:
        for line in infile:
            if line[0] != "#":
                line = line.split("\t")
                mlst_dict[line[1].lower()] = line[0]

    if specie == "escherichia coli":
        mlst_dict['escherichia coli'] = 'ecoli'


    if specie in mlst_dict:
        cmd = "mkdir {}/mlstresults".format(moss_object.target_dir)
        os.system(cmd)
        cmd = "python3 /opt/moss/mlst/mlst.py -i {} -o {}mlstresults" \
              " -mp ~/bin/kma -p /opt/moss/mlst/mlst_db/ -s {} -nano"\
            .format(moss_object.input_path, moss_object.target_dir, mlst_dict[specie])
        os.system(cmd)
        moss_object.mlst = specie

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

def kma_mapping(moss_object):
    os.system("~/bin/kma -i {} -o {}kma_mapping -t_db {}/REFDB.ATG"
              " -ID 0 -nf -mem_mode -sasm -ef -1t1".format(moss_object.input_path, moss_object.target_dir, moss_object.config_path))
    num_lines = sum(1 for line in open("{}kma_mapping.res".format(moss_object.target_dir))) #1 line is empty, more have hits.
    template_score = 0
    if num_lines > 1:
        moss_object.reference_header_text = None
        with open("{}kma_mapping.res".format(moss_object.target_dir)) as infile:
            for line in infile:
                line = line.rstrip()
                line = line.split("\t")
                if line[0][0] != "#":
                    if float(line[1]) > template_score:
                        template_score = float(line[1])
                        moss_object.reference_header_text = line[0]
        template_number = findTemplateNumber(moss_object.config_path, moss_object.reference_header_text)
        moss_object.template_number = template_number
        moss_object.reference_header_text = moss_object.reference_header_text
        if " " in moss_object.reference_header_text:
            moss_object.accesion = moss_object.reference_header_text.split(" ")[0]
        else:
            moss_object.accesion = moss_object.reference_header_text
        moss_object.consensus_name = "{}_{}_consensus.fsa".format(moss_object.sample_name, moss_object.accesion)

        return moss_object
    else:
        print("None of the given templates matches any of the entries in given ref_kma_database."
              " The input reads will now be assembled and added to the reference ref_kma_database as a new reference.")
        moss_object.template_number = None
        moss_object.reference_header_text = None
        return moss_object

def nanopore_alignment(moss_object):
    cmd = "~/bin/kma -i {} -o {}{} -t_db {}/REFDB.ATG -mint3 -Mt1 {} -t 8"\
        .format(moss_object.input_path, moss_object.target_dir, moss_object.consensus_name[:-4],
                moss_object.config_path, str(moss_object.template_number))
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

def ThreshholdDistanceCheck(distancematrixfile, moss_object):
    infile = open(distancematrixfile, 'r')
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == moss_object.consensus_name or line[0] == moss_object.header_name:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == moss_object.consensus_name or line[0] == moss_object.header_name:
                index = linecount
                secondentry = True
        linecount += 1
    return None

def flye_assembly(moss_object):
    cmd = "docker run --name assembly_{0} -v {1}:/tmp/{2} staphb/flye flye -o /tmp/assembly_results" \
          " --threads 8 --nano-raw /tmp/{2}"\
        .format(moss_object.entry_id, moss_object.input_path, moss_object.input_file)
    print (cmd)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_", moss_object.entry_id, shell=True, stdout=subprocess.PIPE))
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/assembly_results {}.".format(id, moss_object.target_dir)
    os.system(cmd)
    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    # Concatenate contigs
    with open("{}assembly_results/assembly.fasta".format(moss_object.target_dir), 'r') as infile:
        with open("{}{}_assembly.fasta".format(moss_object.target_dir, moss_object.sample_name), 'w') as outfile:
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line

            if moss_object.reference_header_text.startswith(">Assembly"):
                new_header_text = ">{}_Assembly_{}".format(moss_object.reference_id, moss_object.reference_header_text[1:]
                                                           .split("_Assembly_")[-1])
            else:
                new_header_text = ">{}_Assembly_{}".format(moss_object.reference_id, moss_object.reference_header_text[1:])
            print(new_header_text, file=outfile)
            print(sequence, file=outfile)

    os.system("~/bin/kma index -t_db {} -i {}{}_assembly.fasta"\
        .format(moss_object.ref_db, moss_object.target_dir, moss_object.sample_name))


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

def compileReportAssembly(moss_object):
    pdf = FPDF()  # A4 (210 by 297 mm)
    filename = "{}_report.pdf".format(moss_object.entry_id)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, moss_object.entry_id, "MOSS analytical report")
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    textstring = "ID: {} \n" \
                 "Suggested reference: {} \n\n" \
                 "No related phylogeny cluster was identified. \n" \
                 "".format(moss_object.entry_id, moss_object.associated_species) #What do we do here? How do we assign a name to a reference assembly? Manuel or automatic?
    pdf.multi_cell(w=155, h=5, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(20)

    run_quast(moss_object.target_dir, moss_object.entry_id)

    df = pd.read_csv(moss_object.target_dir + "quast_output/report.tsv", sep='\t')

    df_styled = df.style.background_gradient()  # adding a gradient based on values in cell
    dfi.export(df_styled, moss_object.target_dir + "quast_table.png")
    pdf.image("{}quast_table.png".format(moss_object.target_dir), x=10, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)
    run_bandage(moss_object.target_dir, moss_object.entry_id)
    pdf.set_xy(x=10, y=58)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(51, 153, 255)
    pdf.image("{}contigs.jpg".format(moss_object.target_dir), x=115, y=90, w=pdf.w / 2.5, h=pdf.h / 2.7)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, moss_object.entry_id, "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    csv_data = derive_amr_stats(moss_object.resfinder_hits, "resfinder_db")

    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    csv_data = derive_virulence_stats(moss_object.virulence_hits,
                                                           "virulencefinder_db", moss_object.target_dir)
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in moss_object.plasmid_hits:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.set_font('Arial', '', 12)

    pdf.output(moss_object.target_dir + filename, 'F')

def mlst_sequence_type(target_dir):
    try:
        with open(target_dir + "mlstresults/data.json") as json_file:
            data = json.load(json_file)
        sequence_type = data['mlst']['results']['sequence_type']
        return sequence_type
    except:
        return "No MLST Found"

def compileReportAlignment(moss_object):
    pdf = FPDF()  # A4 (210 by 297 mm)

    filename = "{}_report.pdf".format(moss_object.entry_id) #ADD idd
    clusterSize = len(moss_object.isolate_list)

    ''' First Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)

    create_title(pdf, moss_object.entry_id, "MOSS analytical report")
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)

    textstring = "ID: {} \n" \
                 "sample_name: {} \n" \
                 "Identified reference: {} \n" \
                 "".format(moss_object.entry_id, moss_object.sample_name, moss_object.reference_header_text)
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
                 "".format(len(moss_object.resfinder_hits), len(moss_object.plasmid_hits), len(moss_object.virulence_hits), moss_object.mlst_type)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)
    pdf.ln(5)

    pdf.set_xy(x=105, y=65)

    ''' Second Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w/8.5, h=pdf.h/8.5)
    create_title(pdf, moss_object.entry_id, "CGE Finder results")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Antimicrobial Genes Found:", 0, 1, 'L')

    csv_data = derive_amr_stats(moss_object.resfinder_hits, "resfinder_db")


    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Virulence Genes Found: ", 0, 1, 'L')

    csv_data = derive_virulence_stats(moss_object.virulence_hits, "virulencefinder_db", moss_object.target_dir)
    line_height = pdf.font_size * 3
    col_width = pdf.w / 4  # distribute content evenly
    lh_list = []  # list with proper line_height for each row
    use_default_height = 0  # flag

    for row in csv_data:
        for datum in row:
            word_list = datum.split()
            number_of_words = len(word_list)  # how many words
            if number_of_words > 2:  # names and cities formed by 2 words like Los Angeles are ok)
                use_default_height = 1
                new_line_height = pdf.font_size * (number_of_words / 1.3)  # new height change according to data
        if not use_default_height:
            lh_list.append(line_height)
        else:
            lh_list.append(new_line_height)
            use_default_height = 0

    # create your fpdf table ..passing also max_line_height!
    for j, row in enumerate(csv_data):
        for datum in row:
            line_height = lh_list[j]  # choose right height for current row
            pdf.multi_cell(col_width, line_height, datum, border=1, align='L', ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)

    pdf.ln(10)

    pdf.cell(85, 5, "Plasmids Found:", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    textstring = ""
    for item in moss_object.plasmid_hits:
        textstring += "* {}\n".format(item)
    pdf.multi_cell(w=85, h=7, txt=textstring, border=0, align='L', fill=False)

    pdf.set_font('Arial', '', 12)

    ''' Third Page '''
    pdf.add_page()
    pdf.image("/opt/moss/local_app/images/DTU_Logo_Corporate_Red_RGB.png", x=175, y=10, w=pdf.w / 8.5, h=pdf.h / 8.5)
    create_title(pdf, moss_object.entry_id, "Cluster phylogeny:")

    pdf.set_font('Arial', '', 10)

    pdf.ln(10)

    pdf.cell(85, 5, "Phylo tree for cluser {}: ".format(moss_object.reference_header_text.split("\t")[0]), 0, 1, 'L')

    moss_object = create_phylo_tree(moss_object)

    pdf.image("{}/phytree_output/tree.png".format(moss_object.target_dir), x=10, y=55, w=pdf.w / 1.5, h=pdf.h / 1.75)

    pdf.output(moss_object.target_dir + filename, 'F')

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