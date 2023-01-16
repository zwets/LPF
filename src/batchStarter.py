"""Wrapper for running multiple analysis. Currently, parallel analysis is not enabled."""
import sys
import os
import argparse
from joblib import Parallel, delayed
import json


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-json', action="store", type=str, dest='json', default="",
                    help='json file')
parser.add_argument('-analysis_type', action="store",
                                 type=str, dest='analysis_type', default="bacteria",
                                 help='bacteria, viral or metagenomic')
args = parser.parse_args()

def moss_analysis(jobslist, i):
    """Start analysis"""
    os.system(jobslist[i])

def main(analysis_type, json_file):
    """Main func"""
    with open(json_file) as infile:
        data = json.load(infile)
    jobslist = []

    for item in data['batch_runs']:
        if os.path.exists('/opt/moss/moss'):
            cmd = 'python3 /opt/moss/moss {} -json {}'.format(analysis_type, item)
        else:
            cmd = 'python3 moss {} -json {}'.format(analysis_type, item)
        #cmd = 'python3 /opt/moss/src/moss.py -json \'{}\''.format(str(item).replace("\'", "\""))
        jobslist.append(cmd)
        #entry_id = moss.md5_of_file(item['input_path'])

        #moss.sql_execute_command(
        #    "INSERT INTO status_table(entry_id, sample_name, status,"
        #    " type, current_stage, final_stage, result, time_stamp)"
        #    " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
        #    .format(entry_id, item['input_path'].split("/")[-1][0:-9], "Analysis waiting.", "Queued", "Queued",
        #            "Queued", "Queued", ""), item['config_path'] + 'moss.db')
    print (jobslist)
    Parallel(n_jobs=1)(delayed(moss_analysis)(jobslist, i) for i in range(len(jobslist))) #Can be changed to parallelize
if __name__== "__main__":
    main(args.analysis_type, args.json)
