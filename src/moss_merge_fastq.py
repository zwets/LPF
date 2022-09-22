import os
import sys
import argparse


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='MOSS 1.1.0')
parser.add_argument("-folder", action="store", type=str, default = "", dest="folder", help="folder")
parser.add_argument("-name", action="store", type=str, default = "", dest="name", help="name")
args = parser.parse_args()

def merge():
    sys.exit(args.folder)
    existing_list = os.path.listdir("/opt/moss_data/")
    if args.name in existing_list:
        sys.exit('There is already a file with that name in the moss_data folder. Please choose a different name.')
    for item in sequencing_list:
        if item not in black_list and item not in existing_list:
            complete_list.append(item)

    for item in complete_list:
        barcode_list = os.path.listdir("/var/lib/minknow/data/" + item + "/reads/")
        os.system("cat /var/lib/minknow/data/" + item + "/*/*/fastq_pass/* > /opt/moss_data/" + item + ".fastq.gz")


def main():
    if __name__ == "__main__":
        merge()