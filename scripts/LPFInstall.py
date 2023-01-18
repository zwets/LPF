import os
import sys
import subprocess
from pathlib import Path



def LPF_installation(arguments):
    """Checks if the databases are installed"""
    proc = subprocess.Popen("whoami", shell=True,
                            stdout=subprocess.PIPE, )
    user = proc.communicate()[0].decode().rstrip()
    if user == "root":
        print(
            bcolors.FAIL + "This script should not be run as root, please run as a normal user. This means DO NOT put sudo in the command line when running ./moss_install, as it will ruin your user path" + bcolors.ENDC)
        sys.exit()
    if not os.path.exists('/home/{}/bin'.format(user)):
        os.system('sudo mkdir /home/{}/bin'.format(user))
    add_bin_path()

    mkfs_LPF()
    print (bcolors.OKGREEN + "LPF filesystem created" + bcolors.ENDC)
    if arguments.complete:
        pass
    elif arguments.install_databases:
        install_databases(arguments)

    check_all_deps()

def add_bin_path():
    infile = open(os.path.expanduser("~/.bashrc"), "r")
    data = infile.read()
    infile.close()
    data = data.split("\n")
    if "export PATH=$PATH:~/bin" not in data:
        print ("Adding ~/bin to PATH")
        os.system("echo \'export PATH=$PATH:~/bin\' >> ~/.bashrc")
        os.system("source ~/.bashrc")

def check_all_deps():
    os.system("cd /opt/moss")
    conda_result = check_conda()
    ont_check = check_ont_deps()
    docker_images_result = check_docker_images()
    pip_deps_result = check_pip_deps()
    local_software_result = check_local_software()
    local_database_result = check_local_database()
    google_chrome_result = check_google_chrome()
    app_build_result = check_app_build()
    v_env_result = check_virtual_env()

    print("\n")
    print("Total dependencies check result:")

    check_list = ["ONT dependencies", "Docker images", "Pip dependencies", "Google Chrome", "Local App", "Conda", "Local software", "Local databases"]
    for item in check_list:
        if item == "ONT dependencies":
            if ont_check:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Docker images":
            if docker_images_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Pip dependencies":
            if pip_deps_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Google Chrome":
            if google_chrome_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(item + " is not installed")
        elif item == "Local App":
            if app_build_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(item + " is not installed")
        elif item == "Conda":
            if conda_result:
                print(bcolors.OKGREEN + item + " is installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Local software":
            if local_software_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Local databases":
            if local_database_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
def check_ont_deps():
    check_list = [
        '/opt/ont',
        '/opt/ont/guppy',
        '/opt/ont/minknow',
        '/lib/systemd/system/guppyd.service'
    ]
    for item in check_list:
        if os.path.exists(item):
            print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
        else:
            print(item + " is not installed")
            return False
    return True

def check_pip_deps():
    pip_list = [
        "geocoder",
        "geopy",
        "nominatim",
        "tabulate",
        "biopython",
        "cgecore",
        "dataframe-image",
        "fpdf2",
    ]
    proc = subprocess.Popen("pip list", shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().split("\n")
    for item in output[0:-1]:
        item = item.split()
        name = item[0]
        if name in pip_list:
            print(bcolors.OKGREEN + name + " is installed" + bcolors.ENDC)
            pip_list.remove(name)
    if len(pip_list) > 0:
        print("The following pip packages are missing:")
        for item in pip_list:
            print(item)
        return False
    else:
        return True

def check_local_database():
    if not os.path.exists('/opt/moss_databases/resfinder_db/resfinder_db.name'):
        print(bcolors.FAIL + "Resfinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/moss_databases/plasmidfinder_db/plasmidfinder_db.name'):
        print(bcolors.FAIL + "Plasmidfinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/moss_databases/virulencefinder_db/virulencefinder_db.name'):
        print(bcolors.FAIL + "Virulencefinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/moss_databases/mlst_db/mlst_db.name'):
        print(bcolors.FAIL + "MLST database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/moss_databases/bacteria_db/bacteria_db.name'):
        print(bcolors.FAIL + "Bacteria database not found" + bcolors.ENDC)
        return False
    else:
        print(bcolors.OKGREEN + "All LPF databases are correctly installed." + bcolors.ENDC)
        return True


def check_docker_images():
    docker_list = [
        "biocontainers/figtree:v1.4.4-3-deb_cv1",
        "staphb/quast:5.0.2",
        "nanozoo/bandage:0.8.1--7da3a06",
        "staphb/flye:2.9.1"
    ]
    proc = subprocess.Popen("docker images", shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().split("\n")

    if "REPOSITORY" not in output[0]:
        print("Docker is not installed")
        return False

    for item in output[0:-1]:
        item = item.split()
        name = item[0] + ":" + item[1]
        if name in docker_list:
            print(bcolors.OKGREEN + name + " are installed" + bcolors.ENDC)
            docker_list.remove(name)
    if len(docker_list) > 0:
        print ("The following docker images are missing:")
        for item in docker_list:
            print (item)
        return False
    else:
        return True

def check_conda():
    home = str(Path.home())
    proc = subprocess.Popen("which conda", shell=True,
                            stdout=subprocess.PIPE, )
    conda_output = proc.communicate()[0].decode().rstrip()
    if (conda_output.startswith(home)):
        print (bcolors.OKGREEN + "Conda is installed corrently in /home/user/" + bcolors.ENDC)
        return True
    else:
        print(bcolors.FAIL + "Conda is not installed" + bcolors.ENDC)
        return False

def check_kma():
    home = str(Path.home())
    if not os.path.exists('{}/bin/kma'.format(home)):
        print(bcolors.FAIL + "KMA not found in bin" + bcolors.ENDC)
        return False
    else:
        print(bcolors.OKGREEN + "KMA is installed" + bcolors.ENDC)
        return True

def check_ccphylo():
    home = str(Path.home())
    if not os.path.exists('{}/bin/ccphylo'.format(home)):
        print(bcolors.FAIL + "CCPHYLO not found in bin" + bcolors.ENDC)
        return False
    else:
        print(bcolors.OKGREEN + "CCPHYLO is installed" + bcolors.ENDC)
        return True

def check_local_software():
    kma_result = check_kma()
    ccphylo_result = check_ccphylo()
    if kma_result and ccphylo_result:
        return True
    else:
        return False

def check_virtual_env():
    proc = subprocess.Popen("conda env list", shell=True,
                            stdout=subprocess.PIPE, )
    env = proc.communicate()[0].decode().split()
    if 'moss' in env:
        print(bcolors.OKGREEN + "Moss environment is installed" + bcolors.ENDC)
        return True
    else:
        print(bcolors.FAIL + "Moss environment is not installed" + bcolors.ENDC)
        return False

def check_app_build():
    path_list = ["/opt/moss_db", "/opt/moss_data", "/opt/moss_databases", "/opt/moss_reports"]
    for item in path_list:
        if not os.path.exists(item):
            print(bcolors.FAIL+ item +" is not installed" + bcolors.ENDC)
            return False
    if check_dist_build():
        return True
    else:
        print ("Local App is not installed")
        return False


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
                     "virulencefinder_db",
                     "mlst_db",
                     "bacteria_db"]

    for item in database_list:
        if not os.path.exists('/opt/moss_databases/{}'.format(item)):
            os.system("sudo mkdir -m 777 /opt/moss_databases/{}".format(item))
        if not os.path.exists('/opt/moss_databases/{}/{}.name'.format(item, item)):
            os.chdir('/opt/moss_databases/{}'.format(item))
            os.system("sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/export/{0}.fasta.gz".format(item))
            if item == 'bacteria_db':
                os.system("kma index -i {}.fasta.gz -o {} -m 14 -Sparse ATG".format(item, item))
            else:
                os.system("kma index -i {}.fasta.gz -o {} -m 14".format(item, item))

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

def check_google_chrome():
    proc = subprocess.Popen("apt list --installed | grep \"google-chrome\"", shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().split("\n")
    for item in output[0:-1]:
        if item.startswith("google-chrome"):
            print("Google Chrome" + " is installed")
            return True
    print("Google Chrome is not installed")
    return False



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
