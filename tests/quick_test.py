import os

def clean_up(md5_list):
    for item in md5_list:
        if os.path.exists():
            os.system("sudo rm -rf {}".format(item))

if __name__ == '__main__':
    md5_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb']
    clean_up(md5_list)
    os.system('python3 /opt/moss/src/batchStarter.py -analysis_type bacteria -batch_json /opt/moss/tests/fixtures/data_for_tests/batchRuns.json')