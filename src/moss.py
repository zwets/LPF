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
        self.validate_object()

    def validate_object(self):
        print('Validating input')
        if not self.input_file in self.input_path:
            raise SystemExit('Input file does not match the input path.')
        if not self.input_path.endswith('.fastq.gz'):
            raise SystemExit('Input is not a fastq.gz file. Only this format is supported.')
        if not self.config_path.startswith('/opt/moss_db'):
            raise SystemExit('An invalid config_path was given.')
        moss.validate_date_text(self.collection_date)
        print('Validation complete')
        return True

def moss_pipeline(moss_object):
    """
    Workflow for analysis pipeline
    """
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
