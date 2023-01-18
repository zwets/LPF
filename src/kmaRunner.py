import logging
import os
import sys
import subprocess
from pathlib import Path

class KMARunner():
    def __init__(self, input, output, reference_database, argument_string):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.check_for_kma()
        self.input = input
        self.output = output
        self.reference_database = reference_database
        self.argument_string = argument_string


    def check_for_kma(self):
        """Checks if kma is installed"""
        try:
            subprocess.call(["{}/bin/kma".format(str(Path.home()))])
        except FileNotFoundError:
            self.logger.info("kma is not installed in the local bin ~/bin/")
            sys.exit(1)

    def run(self):
        """runs kma"""
        self.logger.info("Performing KMA alignment against reference database: ".format(self.reference_database))
        kma_cmd = "{}/bin/kma -t_db {} -i {} -o {} {}".format(str(Path.home()), self.reference_database, self.input, self.output, self.argument_string)
        os.system(kma_cmd)
        self.logger.info(kma_cmd)