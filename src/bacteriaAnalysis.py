###############################################################################
# Pipeline for bacteria analysis
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



def bacteria_analysis_pipeline(bacteria_parser):
    """Runs the bacteria analysis pipeline"""
    sqlCommands.sql_update_status_table('Analysis started', bacteria_parser.data.sample_name, '1', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)
    sqlCommands.sql_execute_command("INSERT INTO sample_table(entry_id, sample_type) VALUES('{}', '{}')".format(bacteria_parser.data.entry_id, 'bacteria'), bacteria_parser.data.sql_db)
    sqlCommands.sql_update_status_table('Reference mapping', bacteria_parser.data.sample_name, '2', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    KMARunner(bacteria_parser.data.input_path,
        bacteria_parser.data.target_dir + "/reference_mapping",
        bacteria_parser.data.bacteria_db,
        "-ID 0 -nf -mem_mode -sasm -ef -1t1").run()

    sqlCommands.sql_update_status_table('ResFinder mapping', bacteria_parser.data.sample_name, '3', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    KMARunner(bacteria_parser.data.input_path,
        bacteria_parser.data.target_dir + "/finders/resfinder_mapping",
        bacteria_parser.data.resfinder_db,
        "-ont -md 5").run()

    sqlCommands.sql_update_status_table('PlasmidFinder mapping', bacteria_parser.data.sample_name, '4', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    KMARunner(bacteria_parser.data.input_path,
        bacteria_parser.data.target_dir + "/finders/plasmidfinder_mapping",
        bacteria_parser.data.plasmidfinder_db,
        "-ont -md 5").run()

    sqlCommands.sql_update_status_table('VirulenceFinder mapping', bacteria_parser.data.sample_name, '5', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    KMARunner(bacteria_parser.data.input_path,
        bacteria_parser.data.target_dir + "/finders/virulencefinder_mapping",
        bacteria_parser.data.virulencefinder_db,
        "-ont -md 5").run()

    bacteria_parser.get_reference_mapping_results()

    # Eval reference hit
    bacteria_parser.parse_finder_results()

    sqlCommands.sql_update_status_table('MLST mapping', bacteria_parser.data.sample_name, '6', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    bacteria_parser.data.species, bacteria_parser.data.mlst_species = mlst.derive_mlst_species(bacteria_parser.data.reference_header_text)
    bacteria_parser.logger.info("MLST species: {}".format(bacteria_parser.data.mlst_species))

    kmergenetyperRunner(bacteria_parser.data.input_path,
                        '{0}/{1}/{1}'.format(bacteria_parser.data.mlst_db, bacteria_parser.data.mlst_species),
                        3,
                        bacteria_parser.data.target_dir + "/finders/mlst").run()

    bacteria_parser.get_mlst_type()

    if bacteria_parser.data.mlst_type != None:
        print ("MLST result: {}".format(bacteria_parser.data.mlst_type))

    if bacteria_parser.data.template_number == None: #No reference template found
        bacteria_parser.run_assembly() #TBD

    sqlCommands.sql_update_status_table('Reference alignment', bacteria_parser.data.sample_name, '7', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    bacteria_parser.single_template_alignment_bacteria()

    bacteria_parser.get_list_of_isolates()

    bacteria_parser.data.isolate_list.append(bacteria_parser.data.consensus_sequence_path) #Consensus sequence

    sqlCommands.sql_update_status_table('Calculating distance matrix', bacteria_parser.data.sample_name, '8', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)


    inclusion_fraction, distance = ccphyloUtils.ccphylo_dist(bacteria_parser)

    if distance == None:
        bacteria_parser.run_assembly()
    elif distance > 300:# or inclusion_fraction < 0.25: #TBD FIX INCLUSION FRACTION
        bacteria_parser.run_assembly()

    sqlCommands.sql_update_status_table('Generating phylogenetic tree', bacteria_parser.data.sample_name, '9', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    if len(bacteria_parser.data.isolate_list) > 3:
        ccphyloUtils.ccphylo_tree(bacteria_parser)
    else:
        bacteria_parser.logger.info("Not enough associated isolates with this cluster for generating a phylogenetic tree")

    sqlCommands.sql_update_status_table('Generating report', bacteria_parser.data.sample_name, '10', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    preparePDF.prepare_alignment_pdf(bacteria_parser)
    pdfReport.compile_alignment_report(bacteria_parser)

    sqlCommands.sql_update_status_table('Analysis completed', bacteria_parser.data.sample_name, '10', bacteria_parser.data.entry_id, bacteria_parser.data.sql_db)

    return 0







