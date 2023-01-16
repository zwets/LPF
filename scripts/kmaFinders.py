import logging
import os

def kma_finders(reference_database, input_path, output_path, argument_string):
    """Runs the kma finders"""
    try:
        logger = logging.getLogger()
        logger.info("Performing KMA alignment against reference database: ".format(reference_database))
    except Exception as error:
        print(error)
    os.system("~/bin/kma -i {} -o {} -t_db {} {}".format(input_path, output_path, reference_database, argument_string))
