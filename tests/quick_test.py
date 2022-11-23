import os
os.system("sudo rm -rf /opt/moss_db/test")
os.system("sudo git pull")
os.system("python3 /opt/moss/src/moss_init.py -db /opt/moss/tests/fixtures/data_for_tests/database/ -config test")
print ("TESTING ALIGNMENT")
os.system("python /opt/moss/src/moss_parallel_wrapper.py -json /opt/moss/tests/fixtures/data_for_tests/json/alignment_test.json")
print ("TESTING ASSEMBLY")
os.system("python /opt/moss/src/moss_parallel_wrapper.py -json /opt/moss/tests/fixtures/data_for_tests/json/assembly_test.json")