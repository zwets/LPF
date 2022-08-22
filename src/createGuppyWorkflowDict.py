import os
import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description='MinION-Typer-2.0')
parser.add_argument("-current_working_db", action="store", dest="current_working_db", help="Enter a name for your configuration file.")
args = parser.parse_args()

cmd = "/opt/ont/guppy/bin/guppy_basecaller --print_workflows > /opt/moss/local_app/tmpworkflowdict.txt"
os.system(cmd)

infile = open("/opt/moss/local_app/static_files/tmpworkflowdict.txt", 'r')
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
outfile = open("/opt/moss/local_app/workflow.json", 'w')

print (json.dumps(jsonlist, indent=2), file=outfile)
outfile.close()


cmd = "/opt/ont/guppy/bin/guppy_barcoder --print_kits > /opt/moss/local_app/printkitstmp.txt"
os.system(cmd)

infile = open("/opt/moss/local_app/printkitstmp.txt", 'r')
jsonlist = []
for line in infile:
    if len(line) > 3: #Non emptie/home/meta2s
        if line[3] == "-":
            line = line.rstrip()
            jsonlist.append({
                "barcode": line
            })


infile.close()
outfile = open("/opt/moss/local_app/barcodes.json", 'w')

print (json.dumps(jsonlist, indent=2), file=outfile)
outfile.close()




cmd = "rm /opt/moss/local_app/tmpworkflowdict.txt"
os.system(cmd)

cmd = "rm /opt/moss/local_app/printkitstmp.txt"
os.system(cmd)

