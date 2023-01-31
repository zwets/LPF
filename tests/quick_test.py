import os
import src.sqlCommands as sqlCommands
def clean_up(md5_list):
    for item in md5_list:
        os.system("sudo rm -rf /opt/LPF_logs/{}.log".format(item))
        os.system("sudo rm -rf /opt/LPF_analyses/{}".format(item))
        sqlCommands.sql_execute_command('DELETE FROM status_table WHERE entry_id = "{}"'.format(item))

if __name__ == '__main__':
    md5_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb']
    clean_up(md5_list)
    os.system('python3 /opt/LPF/src/batchStarter.py -analysis_type bacteria -batch_json /opt/LPF/tests/fixtures/data_for_tests/batchRuns.json')