###############################################################################
# Pipeline for Viral analysis
###############################################################################
import logging
import os
import sys
import datetime

from src.kmaRunner import KMARunner
import src.util.ccphyloUtils as ccphyloUtils
import src.sqlCommands as sqlCommands
import src.pdfReport as pdfReport
import src.util.preparePDF as preparePDF
from src.kmergenetyperRunner import kmergenetyperRunner
import src.util.mlst as mlst
from src.prokkaRunner import prokkaRunner



def viral_analysis_pipeline(viral_parser):
    """Runs the viral analysis pipeline"""
    sqlCommands.sql_update_status_table('Analysis started', viral_parser.data.sample_name, '1',
                                        viral_parser.data.entry_id, viral_parser.data.sql_db)
    sqlCommands.sql_execute_command("INSERT INTO sample_table(entry_id, sample_type) VALUES('{}', '{}')"
                                    .format(viral_parser.data.entry_id, 'virus'), viral_parser.data.sql_db)
    sqlCommands.sql_update_status_table('Viral alignment', viral_parser.data.sample_name, '2',
                                        viral_parser.data.entry_id, viral_parser.data.sql_db)

    KMARunner(viral_parser.data.input_path,
              viral_parser.data.target_dir + "/viral_alignment",
              viral_parser.data.viral_db,
              "-ont -ca -1t1 -mem_mode").run()

    #Consider identity and perhaps assemble if its bad:

    sqlCommands.sql_update_status_table('CDD alignment', viral_parser.data.sample_name, '3',
                                        viral_parser.data.entry_id, viral_parser.data.sql_db)

    KMARunner(viral_parser.data.input_path,
              viral_parser.data.target_dir + "/cdd_alignment",
              viral_parser.data.cdd_db,
              "-ont -ca -1t1 -mem_mode").run()

    sqlCommands.sql_update_status_table('Prokka annotation', viral_parser.data.sample_name, '2',
                                        viral_parser.data.entry_id, viral_parser.data.sql_db)

    prokkaRunner(viral_parser.data.sample_name,
                 viral_parser.data.target_dir + "/viral_alignment.fsa",
                 viral_parser.data.entry_id,
                 viral_parser.data.target_dir).run()

    #Phylogenetic analysis
    #Pathogenicy prediction

    #pdfReport.compile_viral_report(viral_parser)

    sqlCommands.sql_update_status_table('Analysis completed', viral_parser.data.sample_name, '10', viral_parser.data.entry_id, viral_parser.data.sql_db)

    return 0







