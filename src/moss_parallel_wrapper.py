"""Wrapper for running multiple analysis. Currently, parallel analysis is not enabled."""
import sys
import os
import argparse
import moss_functions as moss
from joblib import Parallel, delayed
import json

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-json', action="store", type=str, dest='json', default="",
                    help='json file')
args = parser.parse_args()

def moss_analysis(jobslist, i):
    """Start analysis"""
    os.system(jobslist[i])

def main(json_file):
    """Main func"""
    with open(json_file) as infile:
        data = json.load(infile)
    jobslist = []

    for item in data['samples']:
        cmd = 'python3 /opt/moss/src/moss.py -json \"{}\"'.format(item.replace("\'", "\""))
        jobslist.append(cmd)
        entry_id = moss.md5_of_file(item['input_path'])
        # moss.sql_execute_command(
        #     "INSERT INTO status_table(entry_id, sample_name, status,"
        #     " type, current_stage, final_stage, result, time_stamp)"
        #     " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
        #     .format(entry_id, item['sample_name'], "Queued", "Queued", "Queued",
        #             "Queued", "Queued", ""), item['config_path'] + 'moss.db')

        print (cmd)
    Parallel(n_jobs=1)(delayed(moss_analysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
    main(args.json)
