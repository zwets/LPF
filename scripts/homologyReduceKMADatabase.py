import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('-version', action='version', version='HMRED 0.0.1')
    parser.add_argument("-single_database", action="store", type=str, default = "", dest="single_database", help="single_database to be homology redcued")
    parser.add_argument("-multiple_dbs", action="store", type=str, default = "", dest="multiple_dbs", help="path to a folder with multiple databases to be homology reduced and combined")
    parser.add_argument("-virus", action='store_true', default = False, dest="virus", help="virus")
    parser.add_argument("-bacteria", action='store_true', default = False, dest="bacteria", help="bacteria")
    parser.add_argument("-kma", action='store', default = "", dest="kma_path", help="path to kma")
    parser.add_argument('-output', action="store", type=str, default = "", dest="output", help='output')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    if args.single_database != "":
        if args.virus:
            calculate_average_length_of_sequences_and_partition_files_in_single_database(args.single_database, args.kma_path, args.output)
        elif args.bacteria:
            pass
    elif args.multiple_dbs != "":
        if args.virus:
            db_list = os.listdir(args.multiple_dbs)
            black_list = ['all_databases', 'Coronaviridae', 'Hepadnaviridae', 'Picornaviridae', 'Reoviridae', 'Unclassified']
            for db in db_list:
                if not db in black_list and not db.startswith('.'):
                    calculate_average_length_of_sequences_and_partition_files_in_single_database('{0}/{1}/{1}'.format(args.multiple_dbs, db), args.kma_path,
                                                                             args.output)
            pass
        elif args.bacteria:
            pass

def homology_reduce_each_file(output):
    file_list = os.listdir(output).sort()
    all_header = []
    for file in file_list:
        with open('{}/{}'.format(output, file), 'r') as f:
            for line in f:
                if line.startswith('>'):
                    all_header.append(line.strip())

    pass

def calculate_average_length_of_sequences_and_partition_files_in_single_database(single_database, kma_path, output):
    sequence_dict = {}
    database_name = single_database.split("/")[-1]
    output = output + "/" + database_name
    if not os.path.exists(output):
        os.mkdir(output)
    else:
        print ("{} already exists".format(output))
        sys.exit(0)
    print ("calculating average length of sequences in {}".format(single_database))
    with open(single_database + '.name', "r") as f:
        index = 1
        for line in f:
            line = line.strip()
            specie = get_species_from_header_virus(line)
            if specie not in sequence_dict:
                length = get_sequence_length_from_header(index, single_database, kma_path)
                sequence_dict[specie] = [length]
            else:
                #100 sequences is enough to get a good estimate
                if len(sequence_dict[specie]) < 100:
                    length = get_sequence_length_from_header(index, single_database, kma_path)
                    sequence_dict[specie].append(length)
            #Print progress
            if index % 1000 == 0:
                print ("Processed {} sequences".format(index))
            index += 1

    #Calculate average length of sequences
    print (sequence_dict)
    average_lengths = calculate_average_lengths(sequence_dict)
    thresholds = get_homology_reduction_thresholds(average_lengths)
    partition_single_database_to_species(single_database, kma_path, output)

def partition_single_database_to_species(single_database, kma_path, output):
    if not os.path.exists(single_database + '.fsa'):
        sys.exit("single_database {} does not exist".format(single_database + '.fsa'))
    with open(single_database + '.fsa', "r") as f:
        existing_species = []
        sequence = ''
        index = 1
        for line in f:
            line = line.strip()
            if line[0] == ">":
                index += 1
                if index % 100 == 0:
                    print("Processed {} sequences for partitioning".format(index))
                if sequence != '':
                    with open(output + '/' + specie + '.fsa', "a") as out:
                        print (sequence, file=out)
                specie = get_species_from_header_virus(line)
                if specie not in existing_species:
                    existing_species.append(specie)
                    with open(output + '/' + specie + '.fsa', "w") as out:
                        print (line, file=out)
                else:
                    with open(output + '/' + specie + '.fsa', "a") as out:
                        print (line, file=out)
            else:
                sequence += line
            #Print progress
        with open(output + '/' + specie + '.fsa', "a") as out:
            print (sequence, file=out)




def get_homology_reduction_thresholds(average_lengths):
    thresholds = {}
    for key in average_lengths:
        thresholds[key] = round(average_lengths[key] * 0.01) #1% of the average length
    return thresholds



def calculate_average_lengths(sequence_dict):
    average_lengths = {}
    for key in sequence_dict:
        if len(sequence_dict[key]) == 0:
            print ("No sequences for {}".format(key))
        else:
            average_lengths[key] = sum(sequence_dict[key]) / len(sequence_dict[key])
    return average_lengths


def get_sequence_length_from_header(index, single_database, kma_path):
    if not os.path.exists(kma_path):
        sys.exit("kma is not installed in {}".format(kma_path))
    cmd = "{} seq2fasta -t_db {} -seqs {}".format(kma_path, single_database, index)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode()
    if output == '':
        sys.exit("Error in kma seq2fasta")
    reference_header_text = output.split("\n")[0][1:]
    sequence = output.split("\n")[1]
    return len(sequence)

def get_species_from_header_virus(header):
    specie = header.split(":")[1]
    if '/' in specie:
        specie = specie.replace('/', '_')
    if ' ' in specie:
        specie = specie.replace(' ', '_')
    return specie




if __name__== "__main__":
    main()