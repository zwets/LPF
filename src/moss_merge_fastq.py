import os
import sys
import argparse


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='MOSS 1.1.0')
parser.add_argument("-config_name", action="store", type=str, default = "", dest="config_name", help="config_name")
args = parser.parse_args()

def merge():
    existing_list = os.path.listdir("/opt/moss_data/")
    black_list = ['core-dump-db', 'intermediate', 'persistance', 'pings', 'user_scripts', 'reads', 'queded_reads']
    sequencing_list = os.path.listdir("/var/lib/minknow/data/")
    complete_list = []
    for item in sequencing_list:
        if item not in black_list and item not in existing_list:
            complete_list.append(item)

    for item in complete_list:
        barcode_list = os.path.listdir("/var/lib/minknow/data/" + item + "/reads/")
        os.system("cat /var/lib/minknow/data/" + item + "/*/*/fastq_pass/* > /opt/moss_data/" + item + ".fastq.gz")


def main():
    if __name__ == "__main__":
        merge()