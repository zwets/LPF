"""
Built in guppy runner for moss client
"""
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-i', action="store", type=str, dest='input', default="", help='input')
parser.add_argument('-name', action="store", type=str, dest='name', default="", help='name')
parser.add_argument('-bk', action="store", type=str, dest='bk', default="", help='bk')
parser.add_argument('-chunks', action="store", type=str, dest='chunks', default="", help='chunks')
parser.add_argument('-c', action="store", type=str, dest='model', default="", help='model')
args = parser.parse_args()

def main(arguments):
    """
    Main call
    """
    check_input_name(arguments)
    os.system("mkdir /opt/moss_data/fastq/{}".format(arguments.name))
    base_call(arguments)

def check_input_name(arguments):
    """
    Checks if experiment name is used
    """
    files = os.listdir("/opt/moss_data/fast5/")
    if arguments.name in files:
        sys.exit("This experiment name has already been used. Please choose another one.")

def base_call(arguments):
    """
    Run Guppy
    """
    cmd = "/opt/ont/guppy/bin/guppy_basecaller -i {}  -s /opt/moss_data/fastq/{}/" \
          " --device \"cuda:0\" --compress_fastq --trim_barcodes --barcode_kits {}".format(
        arguments.input, arguments.name, arguments.bk)
    if "sup" in arguments.model:
        cmd += " -c {} --chunks_per_runner 256".format(arguments.model)
    else:
        cmd += " -c {}".format(arguments.model)
    os.system(cmd)
    dir_list = os.listdir("/opt/moss_data/fastq/{}/pass/".format(arguments.name))
    for item in dir_list:
        cmd = "cat /opt/moss_data/fastq/{0}/pass/{1}/* > /opt/moss_data/fastq/{0}/{0}_{1}.fastq.gz"\
            .format(arguments.name, item)
        os.system(cmd)
    os.system("rm /opt/moss_data/fastq/{}/guppy_basecaller_log*".format(arguments.name))
    os.system("rm /opt/moss_data/fastq/{}/*unclassified*".format(arguments.name))

if __name__ == '__main__':
    main(args)
