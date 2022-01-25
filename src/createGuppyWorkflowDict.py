import os
import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument('-db_dir', action="store", type=str, dest='db_dir', default="", help='db_dir')
parser.add_argument("-exepath", action="store", dest="exepath", default = "", help="Complete path to the moss repo that you cloned, in which your kma and ccphylo folder at located.")

args = parser.parse_args()

cmd = ".{}ont-guppy/guppy_basecaller --print_workflows > {}/analyticalFiles/tmpworkflowdict.txt".format(exepath, args.db_dir)
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


cmd = ".{}ont-guppy/guppy_barcoder --print_kits > {}/analyticalFiles/printkitstmp.txt".format(exepath, args.db_dir)
os.system(cmd)

infile = open("{}/analyticalFiles/printkitstmp.txt".format(args.db_dir), 'r')
jsonlist = []
for line in infile:
    if len(line) > 3: #Non emptie/home/meta2s
        if line[3] == "-":
            line = line.rstrip()
            jsonlist.append({
                "barcode": line
            })


infile.close()
outfile = open("{}/analyticalFiles/barcodes.json".format(args.db_dir), 'w')

print (json.dumps(jsonlist, indent=2), file=outfile)
outfile.close()




cmd = "rm {}/analyticalFiles/tmpworkflowdict.txt".format(args.db_dir)
os.system(cmd)

cmd = "rm {}/analyticalFiles/printkitstmp.txt".format(args.db_dir)
os.system(cmd)

