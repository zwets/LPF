import os
import sys
import argparse


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='MOSS 1.1.0')
parser.add_argument("-folder", action="store", type=str, default = "", dest="folder", help="folder")
parser.add_argument("-name", action="store", type=str, default = "", dest="name", help="name")
args = parser.parse_args()

def merge():
    existing_list = os.path.listdir("/opt/moss_data/")
    if args.name in existing_list:
        sys.exit('There is already a file with that name in the moss_data folder. Please choose a different name.')
    os.system('cat {}*.fastq.gz > /opt/moss_data/{}.fastq.gz'.format(args.folder, args.name))


def main():
    if __name__ == "__main__":
        merge()