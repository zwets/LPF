"""Wrapper for running multiple analysis. Currently, parallel analysis is not enabled."""
import sys
import os
import argparse
import moss_functions as moss
from joblib import Parallel, delayed

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-json', action="store", type=str, dest='json', default="",
                    help='json file')
parser.add_argument('-config_name', action="store", type=str, dest='config_name',
                    default="", help='config_name')
args = parser.parse_args()

def moss_analysis(jobslist, i):
    """Start analysis"""
    os.system(jobslist[i])

def main(json_file, config_name):
    """Main func"""
    with open(json_file) as infile:
        data = json.load(infile)
    print (data)
    sys.exit("Printed json data")
    jobslist = []

    for i in range(len(metadata_list)):
        cmd = "python3 /opt/moss/src/moss.py -config_name {} -metadata \"{}\"" \
              " -metadata_headers \"{}\"".format(config_name, metadata_list[i], metadata_headers)
        jobslist.append(cmd)
        input_file = metadata_list[i].split(",")[-2]
        sample_name = metadata_list[i].split(",")[0]
        entry_id = moss.md5_of_file(input_file)
        moss.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
            .format(entry_id, sample_name, "Queued", "Queued", "Queued",
                    "Queued", "Queued", ""), config_name)

    Parallel(n_jobs=jobs)(delayed(moss_analysis)(jobslist, i) for i in range(len(jobslist)))
    print ("Analysis complete")

if __name__== "__main__":
    main(args.json, args.config_name)
