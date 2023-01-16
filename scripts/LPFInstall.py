import os
import sys
from pathlib import Path



def LPF_installation(arguments):
    """Checks if the databases are installed"""
    mkfs_LPF()
    print (bcolors.OKGREEN + "LPF filesystem created" + bcolors.ENDC)
    if arguments.complete:
        pass
    elif arguments.install_databases:
        install_databases(arguments)

def mkfs_LPF():
    """Makes the LPF filesystem"""
    path_list = ["/opt/moss_db/",
                 "/opt/moss_data/",
                 "/opt/moss_databases/",
                 "/opt/moss_reports/",
                 "/opt/moss_logs/"]
    for item in path_list:
        if not os.path.exists(item):
            os.system("sudo mkdir -m 777 {}".format(item))

def install_databases(arguments):
    """Installs the databases"""
    if not check_local_software:
        print(bcolors.FAIL + "MOSS dependencies are not installed, and databases cant be indexed" + bcolors.ENDC)
        sys.exit()
    database_list = ["resfinder_db",
                     "plasmidfinder_db",
                     "virulencefinder_db"] #Add bacteria_db
    for item in database_list:
        if not os.path.exists('/opt/moss_databases/{}'.format(item)):
            os.system("sudo mkdir -m 777 /opt/moss_databases/{}".format(item))
        if not os.path.exists('/opt/moss_databases/{}/{}.name'.format(item, item)):
            os.chdir('/opt/moss_databases/{}'.format(item))
            os.system("sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/export/{0}.fasta.gz".format(item))



def check_local_software():
    kma_result = check_kma()
    ccphylo_result = check_ccphylo()
    if kma_result and ccphylo_result:
        return True
    else:
        return False

def check_kma():
    if not os.path.exists('{}/bin/kma'.format(str(Path.home()))):
        print(bcolors.FAIL + "KMA not found in bin" + bcolors.ENDC)
        return False
    else:
        print(bcolors.OKGREEN + "KMA is installed" + bcolors.ENDC)
        return True

def check_ccphylo():
    if not os.path.exists('{}/bin/ccphylo'.format(str(Path.home()))):
        print(bcolors.FAIL + "CCPHYLO not found in bin" + bcolors.ENDC)
        return False
    else:
        print(bcolors.OKGREEN + "CCPHYLO is installed" + bcolors.ENDC)
        return True



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
