import os
import argparse
import sys

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

import src.sqlCommands as sqlCommands

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-id', action="store", type=str, dest='id', default="",
                    help='id')
args = parser.parse_args()

def main(arguments):
    clean_up(arguments.id)
def clean_up(id):
    os.system("sudo rm -rf /opt/LPF_logs/{}.log".format(id))
    os.system("sudo rm -rf /opt/LPF_analyses/{}".format(id))
    sqlCommands.sql_execute_command('DELETE FROM status_table WHERE entry_id = \"{}\"'.format(id), '/opt/LPF_databases/LPF.db')
    sqlCommands.sql_execute_command('DELETE FROM meta_data_table WHERE entry_id = \"{}\"'.format(id), '/opt/LPF_databases/LPF.db')
    sqlCommands.sql_execute_command('DELETE FROM sample_table WHERE entry_id = \"{}\"'.format(id), '/opt/LPF_databases/LPF.db')
    sqlCommands.sql_execute_command('DELETE FROM sequence_table WHERE entry_id = \"{}\"'.format(id), '/opt/LPF_databases/LPF.db')

if __name__ == '__main__':
    main(args)