""" Script for creating a static json file for the guppy arguments upon installation."""
import os
import argparse
import json

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument("-current_working_db", action="store", dest="current_working_db",
                    help="Enter a name for your configuration file.")
args = parser.parse_args()

CMD = "/opt/ont/guppy/bin/guppy_basecaller --print_workflows >" \
      " local_app/tmpworkflowdict.txt"
os.system(CMD)

with open("local_app/tmpworkflowdict.txt", 'r') as infile:
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

with open("local_app/workflow.json", 'w') as outfile:
    print (json.dumps(jsonlist, indent=2), file=outfile)


CMD = "/opt/ont/guppy/bin/guppy_barcoder --print_kits > local_app/printkitstmp.txt"
os.system(CMD)

with open("local_app/printkitstmp.txt", 'r') as infile:
    jsonlist = []
    for line in infile:
        if len(line) > 3: #Non emptie/home/meta2s
            if line[3] == "-":
                line = line.rstrip()
                jsonlist.append({
                    "barcode": line
                })


with open("local_app/barcodes.json", 'w') as outfile:
    print (json.dumps(jsonlist, indent=2), file=outfile)


CMD = "rm local_app/tmpworkflowdict.txt"
os.system(CMD)

CMD = "rm local_app/printkitstmp.txt"
os.system(CMD)
