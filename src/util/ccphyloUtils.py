import os
import sys
import subprocess


def ccphylo_dist(bacterial_parser):
    make_ccphylo_folder(bacterial_parser)
    cmd = "~/bin/ccphylo dist --input {0}/phytree_output/* --reference \"{1}\" --min_cov 0.01" \
          " --normalization_weight 0 --output {0}/phytree_output/distance_matrix" \
        .format(bacterial_parser.data.target_dir, bacterial_parser.data.reference_header_text)

    proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    err = proc.communicate()[1].decode().rstrip().split(" ")
    bacterial_parser.logger.info(proc.communicate()[1].decode().rstrip())
    inclusion_fraction = int(err[1])/int(err[3])
    bacterial_parser.logger.info("Inclusion fraction: {}".format(inclusion_fraction))
    distance = ThreshholdDistanceCheck(bacterial_parser)
    bacterial_parser.logger.info("Input consensus sequence distance from reference: {}".format(distance))
    return inclusion_fraction, distance

def ThreshholdDistanceCheck(bacterial_parser):
    if not os.path.exists(bacterial_parser.target_dir + '/phytree_output/distance_matrix'):
        bacterial_parser.logger.info('ERROR: Distance matrix was not created.')
    infile = open(bacterial_parser.target_dir + '/phytree_output/distance_matrix', 'r')
    consensus_name = bacterial_parser.data.sample_name + '.fsa'
    header_name = bacterial_parser.data.reference_header_text.split()[0] + '.fsa'
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == consensus_name or line[0] == header_name:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == consensus_name or line[0] == header_name:
                index = linecount
                secondentry = True
        linecount += 1
    return None

def make_ccphylo_folder(bacterial_parser):
    cmd = "mkdir {}/phytree_output".format(bacterial_parser.data.target_dir)
    os.system(cmd)
    for item in bacterial_parser.data.isolate_list:
        if os.path.exists(item):
            os.system("cp {} {}/phytree_output/.".format(item, bacterial_parser.data.target_dir))
    header_name = bacterial_parser.data.reference_header_text.split()[0] + '.fsa'
    cmd = "~/bin/kma seq2fasta -t_db {} -seqs {} > {}/phytree_output/{}" \
        .format(bacterial_parser.data.bacteria_db, bacterial_parser.data.template_number, bacterial_parser.data.target_dir, header_name)
    os.system(cmd)

# def create_phylo_tree(LPF_object):
#     with open ("{}phytree_output/tree.newick".format(bacterial_parser.data.target_dir)) as fd:
#         data = fd.read()
#     handle = StringIO(data)
#     tree = Phylo.read(handle, "newick")
#     matplotlib.rc('font', size=20)
#     fig = plt.figure(figsize=(20, 20), dpi=80)
#     axes = fig.add_subplot(1, 1, 1)
#     Phylo.draw(tree, axes=axes, do_show=False)
#     plt.savefig("{}/phytree_output/tree.png".format(bacterial_parser.data.target_dir), dpi=100)
#     bacterial_parser.data.phytree_path = "{}/phytree_output/tree.png".format(bacterial_parser.data.target_dir)
#     return LPF_object

# def plot_tree(treedata, output_file):
#     handle = StringIO(treedata)  # parse the newick string
#     tree = Phylo.read(handle, "newick")
#     matplotlib.rc('font', size=6)
#     # set the size of the figure
#     fig = plt.figure(figsize=(15, 15), dpi=100)
#     # alternatively
#     # fig.set_size_inches(10, 20)
#     axes = fig.add_subplot(1, 1, 1)
#     Phylo.draw(tree, axes=axes)
#     plt.savefig(output_file, dpi=100)
# 
#     return
