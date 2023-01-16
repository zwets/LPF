import logging
import os
import json
import sys
import datetime
import src.util.md5 as md5
import pyfastx
from types import SimpleNamespace

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
        self.data.reference_database = "{}/REFDB.ATG".format(self.data.config_path)
        self.data.target_dir = "{}/analysis/{}/".format(self.data.config_path, self.data.entry_id)
        self.data.logfile = self.data.entry_id + ".log"
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
        os.system("mkdir {}".format(self.data.target_dir))
        os.system("mkdir {}/finders".format(self.data.target_dir))
        os.system("mkdir {}/finders_1t1".format(self.data.target_dir))