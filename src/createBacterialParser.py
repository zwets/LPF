import logging
import os
import json
import sys
import datetime
import src.util.md5 as md5
import pyfastx
from types import SimpleNamespace

from scripts.version import __version__

class EmptyDataObject:
    pass

class BacterialParser():
    def __init__(self, file):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        with open(file, 'r') as f:
            data_dict = json.loads(f.read())
        self.data = EmptyDataObject()
        for item in data_dict:
            setattr(self.data, item, data_dict[item])
        self.data.entry_id = md5.md5_of_file(self.data.input_path)
        self.data.sample_name = self.data.input_path.split("/")[-1][0:-9]
        self.data.moss_db = "{}/moss.db".format(self.data.config_path)
        self.data.bacteria_db = "/opt/moss_databases/bacteria_db/bacteria_db"
        self.data.resfinder_db = '/opt/moss_databases/resfinder_db/resfinder_db'
        self.data.plasmidfinder_db = '/opt/moss_databases/resfinder_db/plasmidfinder_db/plasmidfinder_db'
        self.data.virulencefinder_db = '/opt/moss_databases/resfinder_db/virulencefinder_db/virulencefinder_db'
        self.data.target_dir = "/opt/moss_analyses/{}".format(self.data.entry_id)
        self.data.logfile = "/opt/moss_logs/{}".format(self.data.entry_id + ".log")
        self.data.version = __version__
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