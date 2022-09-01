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

def moss_pipeline(input_dict):
    """
    Workflow for analysis pipeline
    """
    input_dict = ast.literal_eval(json.dumps(input_dict))
    try:
        moss.validate_input(input_dict)
        input_dict = moss.moss_init(input_dict)
        moss.moss_run(input_dict)
        r_type = moss.evaluate_moss_run()
        if r_type != None: #Evals if completed correctly
            moss.completed_run_update_sql_database(r_type, input_dict) #Updates status_table is return is 0, else moss.clean_sql_for_moss_run()
        else:
            moss.clean_sql_for_moss_run(input_dict)
            sys.exit(error)
    except Exception as error:
        moss.clean_sql_for_moss_run(input_dict)
        sys.exit(error)


def main():
    input = json.loads(args.json)
    moss_pipeline(input)


if __name__== "__main__":
  main()
