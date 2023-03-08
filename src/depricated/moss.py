"""
Main script for the LPF pipeline.
"""
import sys
import argparse
import json
import LPF_functions as LPF
import LPF_helpers as LPF_helpers
import logging
import os
import ast

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='LPF 1.1.0')
parser.add_argument("-json", action="store", type=str, default = "", dest="json", help="input object")
args = parser.parse_args()

class LPFObject:
    #TBD Generate from template instead
    def __init__(self, json_object):
        for item in json_object:
            setattr(self, item, json_object[item])

        self.entry_id = LPF.md5_of_file(self.input_path)
        self.sample_name = self.input_path.split("/")[-1][0:-9]
        self.LPF_db = "{}/LPF.db".format(self.config_path)
        self.ref_db = "{}/REFDB.ATG".format(self.config_path)
        self.target_dir = "{}/analysis/{}/".format(self.config_path, self.entry_id)
        self.logfile = self.entry_id + ".log"

def LPF_pipeline(LPF_object):
    """
    Workflow for analysis pipeline
    """
    try:
        LPF.LPF_mkfs(LPF_object.config_path, LPF_object.entry_id)
        LPF_helpers.begin_logging(LPF_object.target_dir + LPF_object.logfile)
        LPF.check_unique_entry_id(LPF_object.entry_id, LPF_object.LPF_db)
        LPF.qc_check(LPF_object)
        try:
            LPF.validate_LPF_object(LPF_object)
            LPF_object = LPF.LPF_run(LPF_object)
        except Exception as e:
            logging.error(e, exc_info=True)
            r_type = None
            raise

        r_type = LPF.evaluate_LPF_run(LPF_object)
        if r_type != None: #Evals if completed correctly
            print (r_type)
            LPF.completed_run_update_sql_database(r_type, LPF_object)
            LPF.insert_sql_data_to_db(LPF_object, r_type)
        else:
            os.system(
                "cp {} /opt/LPF_logs/{}".format(LPF_object.target_dir + LPF_object.logfile, LPF_object.logfile))
            LPF.sql_execute_command(LPF.clean_sql_for_LPF_run(LPF_object), LPF_object.LPF_db)
            sys.exit(error)
    except Exception as error:
        os.system(
            "cp {} /opt/LPF_logs/{}".format(LPF_object.target_dir + LPF_object.logfile, LPF_object.logfile))
        LPF.sql_execute_command(LPF.clean_sql_for_LPF_run(LPF_object), LPF_object.LPF_db)
        sys.exit(error)


def main():
    input = json.loads(args.json)
    LPF_object = LPFObject(input)
    LPF_pipeline(LPF_object)


if __name__== "__main__":
  main()
