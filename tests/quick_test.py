import os
os.system("sudo rm -rf /opt/moss_db/test")
os.system("sudo git pull")
os.system("python3 /opt/moss/src/moss_init.py -db /opt/moss/tests/fixtures/data_for_tests/database/ -config test")
os.system("python /opt/moss/src/moss_parallel_wrapper.py -json /opt/moss/tests/fixtures/data_for_tests/json/alignment_test.json")