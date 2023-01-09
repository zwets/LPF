"""
Main script for the moss pipeline.
"""
import sys
import argparse
import json
import moss_functions as moss
import moss_helpers as moss_helpers
import logging
import os
import ast

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='MOSS 1.1.0')
parser.add_argument("-json", action="store", type=str, default = "", dest="json", help="input object")
args = parser.parse_args()

class MossObject:
    #TBD Generate from template instead
    def __init__(self, json_object):
        for item in json_object:
            setattr(self, item, json_object[item])

        self.entry_id = moss.md5_of_file(self.input_path)
        self.sample_name = self.input_path.split("/")[-1][0:-9]
        self.moss_db = "{}/moss.db".format(self.config_path)
        self.ref_db = "{}/REFDB.ATG".format(self.config_path)
        self.target_dir = "{}/analysis/{}/".format(self.config_path, self.entry_id)
        self.logfile = self.entry_id + ".log"

def moss_pipeline(moss_object):
    """
    Workflow for analysis pipeline
    """
    try:
        moss.moss_mkfs(moss_object.config_path, moss_object.entry_id)
        moss_helpers.begin_logging(moss_object.target_dir + moss_object.logfile)
        moss.check_unique_entry_id(moss_object.entry_id, moss_object.moss_db)
        moss.qc_check(moss_object)
        try:
            moss.validate_moss_object(moss_object)
            moss_object = moss.moss_run(moss_object)
        except Exception as e:
            logging.error(e, exc_info=True)
            r_type = None
            raise

        r_type = moss.evaluate_moss_run(moss_object)
        if r_type != None: #Evals if completed correctly
            print (r_type)
            moss.completed_run_update_sql_database(r_type, moss_object)
            moss.insert_sql_data_to_db(moss_object, r_type)
        else:
            os.system(
                "cp {} /opt/moss_logs/{}".format(moss_object.target_dir + moss_object.logfile, moss_object.logfile))
            moss.sql_execute_command(moss.clean_sql_for_moss_run(moss_object), moss_object.moss_db)
            sys.exit(error)
    except Exception as error:
        os.system(
            "cp {} /opt/moss_logs/{}".format(moss_object.target_dir + moss_object.logfile, moss_object.logfile))
        moss.sql_execute_command(moss.clean_sql_for_moss_run(moss_object), moss_object.moss_db)
        sys.exit(error)


def main():
    input = json.loads(args.json)
    moss_object = MossObject(input)
    moss_pipeline(moss_object)


if __name__== "__main__":
  main()
