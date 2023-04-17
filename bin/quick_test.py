import os
import sys

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

import src.sqlCommands as sqlCommands


def clean_up(md5_list):
    for item in md5_list:
        os.system("rm -rf /opt/LPF_logs/{}.log".format(item))
        os.system("rm -rf /opt/LPF_analyses/{}".format(item))
        sqlCommands.sql_execute_command('DELETE FROM status_table WHERE entry_id = \"{}\"'.format(item), '/opt/LPF_databases/LPF.db')
        sqlCommands.sql_execute_command('DELETE FROM meta_data_table WHERE entry_id = \"{}\"'.format(item), '/opt/LPF_databases/LPF.db')
        sqlCommands.sql_execute_command('DELETE FROM sample_table WHERE entry_id = \"{}\"'.format(item), '/opt/LPF_databases/LPF.db')
        sqlCommands.sql_execute_command('DELETE FROM sequence_table WHERE entry_id = \"{}\"'.format(item), '/opt/LPF_databases/LPF.db')

if __name__ == '__main__':
    md5_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb', '83d1531bdc862f7ddbf754221fae6a66']
    clean_up(md5_list)
    os.system('python3 /opt/LPF/src/batchStarter.py -analysis_type bacteria -batch_json /opt/LPF/tests/fixtures/bacteria_batch.json')
    os.system('python3 /opt/LPF/src/batchStarter.py -analysis_type virus -batch_json /opt/LPF/tests/fixtures/virus_batch.json')