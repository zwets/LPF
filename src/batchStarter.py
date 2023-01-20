"""Wrapper for running multiple analysis. Currently, parallel analysis is not enabled."""
import sys
import os
import argparse
import util.md5 as md5
from joblib import Parallel, delayed
import json


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-batch_json', action="store", type=str, dest='batch_json', default="",
                    help='batch json file')
parser.add_argument('-analysis_type', action="store",
                                 type=str, dest='analysis_type', default="bacteria",
                                 help='bacteria, viral or metagenomic')
args = parser.parse_args()

def moss_analysis(jobslist, i):
    """Start analysis"""
    os.system(jobslist[i])

def main(analysis_type, batch_json):
    """Main func"""
    json_list = create_individual_json_files(batch_json)
    jobslist = []
    for item in json_list:
        if os.path.exists('/opt/moss/moss'):
            cmd = 'python3 /opt/moss/moss {} -json {}'.format(analysis_type, item)
        else:
            cmd = 'python3 moss {} -json {}'.format(analysis_type, item)
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

def create_individual_json_files(batch_json):
    """Create individual json files for each sample"""
    with open(batch_json) as infile:
        data = json.load(infile)
    output_list = []
    for item in data['batch_runs']:
        entry_id = md5.md5_of_file(item['input_path'])
        with open("/opt/moss_metadata_json/individual_json/{}.json".format(entry_id), 'w') as outfile:
            json.dump(item, outfile)
        output_list.append("/opt/moss_metadata_json/individual_json/{}.json".format(entry_id))
    return output_list

if __name__== "__main__":
    main(args.analysis_type, args.batch_json)
