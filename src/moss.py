"""
Main script for the moss pipeline.
"""
import sys
import argparse
import json
import moss_functions as moss
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

def moss_pipeline(moss_object):
    """
    Workflow for analysis pipeline
    """
    moss.validate_moss_object(moss_object)
    try:
        moss_object = moss.moss_init(moss_object)
        moss.check_unique_entry_id(moss_object.entry_id, moss_object.moss_db)
        moss.qc_check(moss_object)
        moss_object = moss.moss_run(moss_object)
        r_type = moss.evaluate_moss_run(moss_object)
        if r_type != None: #Evals if completed correctly
            print (r_type)
            moss.completed_run_update_sql_database(r_type, moss_object)
            moss.insert_sql_data_to_db(moss_object, r_type)
        else:
            moss.sql_execute_command(moss.clean_sql_for_moss_run(moss_object), moss_object.moss_db)
            sys.exit(error)
    except Exception as error:
        moss.sql_execute_command(moss.clean_sql_for_moss_run(moss_object), moss_object.moss_db)
        sys.exit(error)


def main():
    input = json.loads(args.json)
    moss_object = MossObject(input)
    moss_pipeline(moss_object)


if __name__== "__main__":
  main()
