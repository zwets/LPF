import os
import subprocess

def flye_assembly(bacterial_parser):
    cmd = "docker run --name assembly_{0} -v {1}:/tmp/{2} staphb/flye flye -o /tmp/assembly_results" \
          " --threads 8 --nano-raw /tmp/{2}"\
        .format(bacterial_parser.data.entry_id, bacterial_parser.data.input_path, bacterial_parser.data.input_file)
    print (cmd)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_", bacterial_parser.data.entry_id), shell=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/assembly_results {}/assembly_results".format(id, bacterial_parser.data.target_dir)
    os.system(cmd)
    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    # Concatenate contigs
    with open("{}/assembly_results/assembly.fasta".format(bacterial_parser.data.target_dir), 'r') as infile:
        with open("{}/{}_assembly.fasta".format(bacterial_parser.data.target_dir, bacterial_parser.data.sample_name), 'w') as outfile:
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line

            if bacterial_parser.data.reference_header_text.startswith(">Assembly"):
                new_header_text = ">{}_Assembly_{}".format(bacterial_parser.data.entry_id, bacterial_parser.data.reference_header_text[1:]
                                                           .split("_Assembly_")[-1])
            else:
                new_header_text = ">{}_Assembly_{}".format(bacterial_parser.data.entry_id, bacterial_parser.data.reference_header_text[1:])
            print(new_header_text, file=outfile)
            print(sequence, file=outfile)

    #test_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb'] #IDs of test files to be ignored
    #if bacterial_parser.data.entry_id not in test_list:
    #    os.system("~/bin/kma index -t_db {} -i {}{}_assembly.fasta"\
    #              .format(bacterial_parser.data.ref_db, bacterial_parser.data.target_dir, bacterial_parser.data.sample_name))