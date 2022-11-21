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
        self.input_file = json_object['input_file']
        self.input_path = json_object['input_path']
        self.sequencing_method = json_object['sequencing_method']
        self.isolation_source = json_object['isolation_source']
        self.investigation_type = json_object['investigation_type']
        self.collection_date = json_object['collection_date']
        self.city = json_object['city']
        self.country = json_object['country']
        self.patient_gender = json_object['patient_gender']
        self.patient_age = json_object['patient_age']
        self.type_of_infection = json_object['type_of_infection']
        self.experimental_condition = json_object['experimental_condition']
        self.config_path = json_object['config_path']
        self.entry_id = json_object['entry_id']
        self.moss_db = json_object['moss_db']
        self.ref_db = json_object['ref_db']
        self.target_dir = json_object['target_dir']

    def validate_object(self):
        #TBD
        return True

    print('Validating input')
    if not input_dict['input_file'] in input_dict['input_path']:
        raise SystemExit('Input file does not match the input path.')
    if not input_dict['input_path'].endswith('.fastq.gz'):
        raise SystemExit('Input is not a fastq.gz file. Only this format is supported.')
    if not input_dict['config_path'].startswith('/opt/moss_db'):
        raise SystemExit('An invalid config_path was given.')
    validate_date_text(input_dict['collection_date'])
    print('Validation complete')


def moss_pipeline(input_dict):
    """
    Workflow for analysis pipeline
    """
    input_dict = ast.literal_eval(json.dumps(input_dict))
    try:
        moss.validate_input(input_dict)
        input_dict = moss.moss_init(input_dict)
        moss.check_unique_entry_id(input_dict['entry_id'], input_dict['moss_db'])
        moss.qc_check(input_dict)
        input_dict = moss.moss_run(input_dict)
        r_type = moss.evaluate_moss_run(input_dict)
        if r_type != None: #Evals if completed correctly
            print (r_type)
            moss.completed_run_update_sql_database(r_type, input_dict)
            moss.insert_sql_data_to_db(input_dict, r_type)
        else:
            moss.sql_execute_command(moss.clean_sql_for_moss_run(input_dict), input_dict['moss_db'])
            sys.exit(error)
    except Exception as error:
        moss.sql_execute_command(moss.clean_sql_for_moss_run(input_dict), input_dict['moss_db'])
        sys.exit(error)


def main():
    input = json.loads(args.json)
    moss_pipeline(input)


if __name__== "__main__":
  main()
