###############################################################################
# Pipeline for bacterial analysis
###############################################################################

import logging
import os
import sys
import datetime

from scripts.kmaFinders import kma_finders
from src.kmaRunner import KMARunner

def bacterial_analysis_pipeline(bacterial_parser):
    """Runs the bacterial analysis pipeline"""
    reference_mapping = KMARunner(bacterial_parser.data.input_path,
                           bacterial_parser.data.target_dir + "/reference_mapping",
                           bacterial_parser.data.bacteria_db,
                           "-ID 0 -nf -mem_mode -sasm -ef -1t1")
    #reference_mapping.run()

    resfinder_mapping = KMARunner(bacterial_parser.data.input_path,
                            bacterial_parser.data.target_dir + "/finders/resfinder_mapping",
                            bacterial_parser.data.resfinder_db,
                            "-ont -md 5")
    #resfinder_mapping.run()

    plasmidfinder_mapping = KMARunner(bacterial_parser.data.input_path,
                            bacterial_parser.data.target_dir + "/finders/plasmidfinder_mapping",
                            bacterial_parser.data.plasmidfinder_db,
                            "-ont -md 5")
    #plasmidfinder_mapping.run()

    virulencefinder_mapping = KMARunner(bacterial_parser.data.input_path,
                            bacterial_parser.data.target_dir + "/finders/virulencefinder_mapping",
                            bacterial_parser.data.virulencefinder_db,
                            "-ont -md 5")
    virulencefinder_mapping.run()