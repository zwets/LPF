
import sys
import os
import argparse

#Rewrite, complete or scrap? Not good idea to implement in system IMO. When would we ever need it?



parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='Batch')
parser.add_argument('-pass_dir', action="store", type=str, dest='pass_dir', default="", help='complete path to directory with pass fast5s')
args = parser.parse_args()

pass_dir = args.pass_dir

if pass_dir[-1] != "/":
    pass_dir += "/"
output = pass_dir[0:-5]



if not os.path.isdir("mkdir {}batches".format(output)):
    os.system("mkdir {}batches".format(output))

file = output+"status.txt"
if not os.path.isfile(file):
    finished_files = []
    os.system("touch {}".format(file))
else:
    finished_files = []
    infile = open(file, 'r')
    for line in infile:
        line = line.rstrip()
        finished_files.append(line)
    infile.close()

all_files = os.listdir(pass_dir)
all_files.sort()

completed_files = all_files[:-1] #Skip newest if writing in process

basecalls = []

for item in completed_files:
    if item not in finished_files:
        basecalls.append(item)
        finished_files.append(item)

batch_number = len(os.listdir("{}/batches".format(output)))+1

os.system("mkdir {}/batches/batch_{}".format(output, batch_number))
os.system("mkdir {}/batches/batch_{}/fast5".format(output, batch_number))

for item in basecalls:
    os.system("cp {}{} {}/batches/batch_{}/fast5/.".format(pass_dir, item, output, batch_number))

outfile = open(file, 'w')
for item in finished_files:
    print (item, file = outfile)
outfile.close()



