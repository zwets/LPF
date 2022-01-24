import os
import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='db_dir')

args = parser.parse_args()

cmd = "docker run genomicpariscentre/guppy-gpu guppy_basecaller --print_workflows > {}/analyticalFiles/tmpworkflowdict.txt".format(args.db_dir)
os.system(cmd)

infile = open("{}/analyticalFiles/tmpworkflowdict.txt".format(args.db_dir), 'r')
jsonlist = []
for line in infile:
    if line[0:3] == "FLO":
        line = line.rstrip()
        if line[0:3] == "FLO":
            line = line.split()
            if line[2] == "included":
                line.pop(2)
            line[2] = line[2].replace('_hac_prom', '')
            line[2] = line[2].replace('_hac', '')
            jsonlist.append({
                "flowcell": line[0],
                "kit": line[1],
                "barcoding_config_name": line[2],
                "model_version": line[3]
            })


infile.close()
outfile = open("{}/analyticalFiles/workflow.json".format(args.db_dir), 'w')

print (json.dumps(jsonlist, indent=2), file=outfile)
outfile.close()
"""
sys.exit()
cmd = "grep \"kits\" /opt/ont/guppy/data/barcoding/*".format(args.db_dir)
proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
output = proc.communicate()[0].decode()

lines = output.split("\n")

barcodes = set()

for item in jsonlist:
    barcodes.add(barcode)

jsonlist = list()
for barcode in barcodes:
    if barcode != "":
        jsonlist.add({
            "barcode": barcode
        })
outfile = open("{}/analyticalFiles/barcodes.json".format(args.db_dir), 'w')

print (json.dumps(jsonlist, indent=2), file=outfile)
outfile.close()

"""


cmd = "rm {}/analyticalFiles/tmpworkflowdict.txt".format(args.db_dir)
os.system(cmd)
