import logging
import os
import json
import sys
import datetime
import src.util.md5 as md5
import pyfastx

import src.sqlCommands as sqlCommands
from types import SimpleNamespace
import src.util.kmaUtils as kmaUtils
from src.kmaRunner import KMARunner
from src.util.assemblyUtils import flye_assembly


from src.loggingHandlers import begin_logging
import src.util.mlst as mlst

from scripts.version import __version__

class EmptyDataObject:
    pass

class BacterialParser():
    def __init__(self, file):
        with open(file, 'r') as f:
            data_dict = json.loads(f.read())
        self.data = EmptyDataObject()
        for item in data_dict:
            setattr(self.data, item, data_dict[item])
        self.data.entry_id = md5.md5_of_file(self.data.input_path)
        begin_logging('/opt/LPF_logs/{}.log'.format(self.data.entry_id))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info("Starting analysis of {}".format(self.data.entry_id))
        self.data.sample_name = self.data.input_path.split("/")[-1][0:-9]
        self.data.bacteria_db = "/opt/LPF_databases/bacteria_db/bacteria_db"
        self.data.resfinder_db = '/opt/LPF_databases/resfinder_db/resfinder_db'
        self.data.plasmidfinder_db = '/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db'
        self.data.virulencefinder_db = '/opt/LPF_databases/virulencefinder_db/virulencefinder_db'
        self.data.mlst_db = '/opt/LPF_databases/mlst_db/mlst_db'
        self.data.sql_db = '/opt/LPF_databases/LPF.db'
        self.data.target_dir = "/opt/LPF_analyses/{}".format(self.data.entry_id)
        self.data.version = __version__
        self.data.black_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb'] #IDs from testfiles to be excluded from SQL and reference indexing
        self.logger.info('BacterialParser initialized with data: {}'.format(self.data.__dict__))
        self.qc_check()
        self.mkfs()

    def __str__(self):
        return str(self.data.__dict__)

    def __repr__(self):
        return self.data.__dict__

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        return self.data[key]

    def qc_check(self):
        """Very basic QC. Only checks for a minimum amount of input data for bacterial analysis"""
        fq = pyfastx.Fastq(self.data.input_path, build_index=False)
        total_bases = 0
        for read in fq:
            total_bases += len(read[1])
        self.logger.info("Total bases in reads: {}. A minimum of 25.000.000 is required.".format(total_bases))
        if total_bases < 25 * 10 ^ 6:
            self.logger.info("Not enough DNA for analysis")
            sys.exit(1)
        else:
            self.logger.info("Enough DNA for analysis. Total bases: {}".format(total_bases))

    def mkfs(self):
        """Creates the target directory and the log file"""
        if not os.path.exists(self.data.target_dir):
            os.makedirs(self.data.target_dir)
            os.makedirs(self.data.target_dir + "/finders")
            os.makedirs(self.data.target_dir + "/finders_1t1/")
        else:
            self.logger.info("Target directory already exists. Sample has been analysed before. Exiting.")
            #Consider not existing but just rerunning the analysis
            sys.exit(1)

    def get_reference_mapping_results(self):
        """Returns the mapping results from the reference mapping"""
        if os.path.exists(self.data.target_dir + "/reference_mapping.res"):
            template_score = 0
            reference_header_text = ""
            with open(self.data.target_dir + "/reference_mapping.res", 'r') as f:
                data = f.read().split("\n")
            data = data[:-1] #Last line is empty
            for item in data:
                item = item.split("\t")
                if item[0][0] != "#":
                    if float(item[1]) > template_score:
                        template_score = float(item[1])
                        reference_header_text = item[0]
            template_number = kmaUtils.findTemplateNumber(reference_header_text, '/opt/LPF_databases/bacteria_db/bacteria_db')
            self.data.template_number = template_number
            self.data.template_score = template_score
            self.data.reference_header_text = reference_header_text

    def get_mlst_results(self):
        """Returns the mlst results"""
        self.data.mlst_species = mlst.derive_mlst_species(self.data.reference_header_text)
        self.data.mlst_result = mlst.determine_mlst(self)

    def run_assembly(self):
        """
        Performing Flye assebly
        """
        self.logger.info('Performing Flye assebly')
        sqlCommands.sql_update_status_table('Performing assembly', self.data.sample_name, '7', self.data.entry_id, self.data.sql_db)

        flye_assembly(self)

        sqlCommands.sql_update_status_table('Assembly completed', self.data.sample_name, '8', self.data.entry_id, self.data.sql_db)


    def single_template_alignment_bacteria(self):
        self.logger.info("Running single template alignment for bacteria")
        template_alignment = KMARunner(self.data.input_path,
                                          self.data.target_dir + "/" + self.data.sample_name,
                                          self.data.bacteria_db,
                                          "-mint3 -Mt1 {} -t 8".format(self.data.template_number))
        template_alignment.run()

        if os.path.exists(self.data.target_dir + "/" + self.data.sample_name + '.fsa'):
            self.logger.info("Single template alignment completed")
            self.data.consensus_sequence_path = self.data.target_dir + "/" + self.data.sample_name + '.fsa'
            header = ''
            sequence = ''
            with open(self.data.consensus_sequence_path, 'r') as f:
                for line in f:
                    if line[0] == '>':
                        header = line[1:].strip()
                    else:
                        sequence += line.strip()
            if header != '' and sequence != '':
                sqlCommands.sql_execute_command("INSERT INTO sequence_table(entry_id, header, sequence) VALUES('{}', '{}', '{}')".format(entry_id, header, sequence), '/opt/LPF_databases/LPF.db')
            else:
                self.logger.info("No consensus sequence found")
        else:
            self.logger.info("No consensus sequence found")

        #handle consensus path
        #Insert consesus into SQL?

    def get_list_of_isolates(self):
        """Returns a list of isolates from the reference template"""
        self.logger.info("Getting list of isolates from reference template")
        self.data.isolate_list = sqlCommands.sql_fetch_all("SELECT isolates FROM bacteria_reference_table WHERE reference_header_text = \"{}\"".format(self.data.reference_header_text), '/opt/LPF_databases/LPF.db')



