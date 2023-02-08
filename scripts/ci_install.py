import os
import sys
import subprocess

from LPFInstall import check_local_software, download_mlst_tables, create_sql_db,  insert_bacterial_references_into_sql

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def ci_install(user, cwd):
    """Installs the databases"""
    if not check_local_software:
        print(bcolors.FAIL + "LPF dependencies are not installed, and databases cant be indexed" + bcolors.ENDC)
        sys.exit()

    database_list = ["resfinder_db",
                     "plasmidfinder_db",
                     "virulencefinder_db",
                     "mlst_db",
                     "bacteria_db"]

    for item in database_list:
        if not os.path.exists('/opt/LPF_databases/{}'.format(item)):
            os.system("sudo mkdir -m 777 /opt/LPF_databases/{}".format(item))
        if not os.path.exists('/opt/LPF_databases/{}/{}.name'.format(item, item)):
            os.chdir('/opt/LPF_databases/{}'.format(item))
            if item == 'bacteria_db':
                os.system('cp tests/fixtures/data_for_tests/database/bacteria_db/* /opt/LPF_databases/bacteria_db/.')
                os.system("kma index -i {}.fasta.gz -o {} -m 14 -Sparse ATG".format(item, item))
            else:
                os.system(
                    "sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/export/{0}.fasta.gz".format(
                        item))
                os.system("kma index -i {}.fasta.gz -o {} -m 14".format(item, item))
        if item == "mlst_db":
            os.chdir('/opt/LPF_databases/{}'.format(item))
            if not os.path.exists('/opt/LPF_databases/{}/config'.format(item)):
                os.system(
                    "sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/config".format(item))
            download_mlst_tables()

    os.chdir(cwd)
    os.system("cp scripts/schemes/notes.txt /opt/LPF_databases/virulencefinder_db/notes.txt")
    os.system("cp scripts/schemes/phenotypes.txt /opt/LPF_databases/resfinder_db/phenotypes.txt")
    if not os.path.exists('/opt/LPF_databases/LPF.db'):
        create_sql_db()
    insert_bacterial_references_into_sql()

