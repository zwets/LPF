###############################################################################
# Pipeline for bacterial analysis
###############################################################################

import logging
import os
import sys
import datetime
from src.kmaRunner import KMARunner
import src.util.ccphyloUtils as ccphyloUtils
import src.sqlCommands as sqlCommands

def bacterial_analysis_pipeline(bacterial_parser):
    """Runs the bacterial analysis pipeline"""
    sqlCommands.sql_update_status_table('Analysis started', bacterial_parser.data.sample_name, '1', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)
    sqlCommands.sql_execute_command("INSERT INTO sample_table(entry_id, sample_type) VALUES('{}', '{}')".format(bacterial_parser.data.entry_id, 'bacteria'), bacterial_parser.data.sql_db)
    sqlCommands.sql_update_status_table('Reference mapping', bacterial_parser.data.sample_name, '2', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    KMARunner(bacterial_parser.data.input_path,
        bacterial_parser.data.target_dir + "/reference_mapping",
        bacterial_parser.data.bacteria_db,
        "-ID 0 -nf -mem_mode -sasm -ef -1t1").run()

    sqlCommands.sql_update_status_table('ResFinder mapping', bacterial_parser.data.sample_name, '3', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    KMARunner(bacterial_parser.data.input_path,
        bacterial_parser.data.target_dir + "/finders/resfinder_mapping",
        bacterial_parser.data.resfinder_db,
        "-ont -md 5").run()

    sqlCommands.sql_update_status_table('PlasmidFinder mapping', bacterial_parser.data.sample_name, '4', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    KMARunner(bacterial_parser.data.input_path,
        bacterial_parser.data.target_dir + "/finders/plasmidfinder_mapping",
        bacterial_parser.data.plasmidfinder_db,
        "-ont -md 5").run()

    sqlCommands.sql_update_status_table('VirulenceFinder mapping', bacterial_parser.data.sample_name, '5', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    KMARunner(bacterial_parser.data.input_path,
        bacterial_parser.data.target_dir + "/finders/virulencefinder_mapping",
        bacterial_parser.data.virulencefinder_db,
        "-ont -md 5").run()

    sqlCommands.sql_update_status_table('MLST mapping', bacterial_parser.data.sample_name, '6', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    KMARunner(bacterial_parser.data.input_path,
        bacterial_parser.data.target_dir + "/finders/mlst_mapping",
        bacterial_parser.data.mlst_db,
        "-ont -md 5").run()

    #1t1?

    bacterial_parser.get_reference_mapping_results()

    #Eval reference hit
    bacterial_parser.parse_finder_results()
    bacterial_parser.get_mlst_results()

    if bacterial_parser.data.mlst_result != "Unknown":
        print ("MLST result: {}".format(bacterial_parser.data.mlst_result))

    if bacterial_parser.data.template_number == None: #No reference template found
        bacterial_parser.run_assembly() #TBD

    sqlCommands.sql_update_status_table('Reference alignment', bacterial_parser.data.sample_name, '7', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    bacterial_parser.single_template_alignment_bacteria()

    bacterial_parser.get_list_of_isolates()

    bacterial_parser.data.isolate_list.append(bacterial_parser.data.consensus_sequence_path) #Consensus sequence

    sqlCommands.sql_update_status_table('Calculating distance matrix', bacterial_parser.data.sample_name, '8', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    inclusion_fraction, distance = ccphyloUtils.ccphylo_dist(bacterial_parser)

    if distance == None:
        bacterial_parser.run_assembly()
    elif distance > 300 or inclusion_fraction < 0.25: #TBD
        bacterial_parser.run_assembly()

    sqlCommands.sql_update_status_table('Generating phylogenetic tree', bacterial_parser.data.sample_name, '9', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    if len(bacterial_parser.data.isolate_list) > 3:
        ccphyloUtils.ccphylo_tree(bacterial_parser)
    else:
        bacterial_parser.logger.info("Not enough associated isolates with this cluster for generating a phylogenetic tree")

    sqlCommands.sql_update_status_table('Generating report', bacterial_parser.data.sample_name, '10', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    #pdf report

    sqlCommands.sql_update_status_table('Analysis completed', bacterial_parser.data.sample_name, '10', bacterial_parser.data.entry_id, bacterial_parser.data.sql_db)

    return 0







