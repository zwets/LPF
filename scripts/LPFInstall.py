import os
import sys
import subprocess
import sqlite3
import src.sqlCommands as sqlCommands
import src.util.md5 as md5
from pathlib import Path
import shutil
import logging
from src.loggingHandlers import begin_logging


def LPF_installation(arguments):
    """Checks if the databases are installed"""
    #install with log:
    #./LocalPathogenFinder install -complete 2>&1 | tee -a LPF_install.log
    print("LPF installation started")

    proc = subprocess.Popen("whoami", shell=True,
                            stdout=subprocess.PIPE, )
    user = proc.communicate()[0].decode().rstrip()
    print("User is {}".format(user))
    if user == "root":
        print(
            bcolors.FAIL + "This script should not be run as root, please run as a normal user. This means DO NOT put sudo in the command line when running ./LPF install, as it will ruin your user path" + bcolors.ENDC)
        print("User is root, exiting")
        sys.exit()
    if not os.path.exists('/home/{}/bin'.format(user)):
        os.system('sudo mkdir /home/{}/bin'.format(user))
    os.system("pip install -r requirements.txt")
    add_bin_path()
    mkfs_LPF()

    print(bcolors.OKGREEN + "LPF filesystem created" + bcolors.ENDC)
    cwd = os.getcwd()
    print("Current working directory is {}".format(cwd))
    if arguments.complete:
        solve_conda_env()
        print(bcolors.OKGREEN + "LPF environment created" + bcolors.ENDC)
        install_ont_deps()
        print(bcolors.OKGREEN + "ONT dependencies installed" + bcolors.ENDC)
        install_LPF_deps(user)
        print(bcolors.OKGREEN + "LPF dependencies installed" + bcolors.ENDC)
        install_databases(arguments, cwd)
        os.chdir(cwd)
        print(bcolors.OKGREEN + "Databases installed" + bcolors.ENDC)
        LPF_build_app()
        print(bcolors.OKGREEN + "LPF app built" + bcolors.ENDC)
    elif arguments.install_ont_deps:
        solve_conda_env()
        install_ont_deps()
    elif arguments.app:
        reinstall_app()
    elif arguments.install_databases:
        install_databases(arguments, cwd)
        os.chdir(cwd)
    elif arguments.ci:
        solve_conda_env()
        install_LPF_deps(user)
        ci_install(user, cwd)
        sys.exit()
    check_all_deps()
    check_and_add_bookmarks()
    print('Installation complete')





def build_app():
    if os.path.exists("/usr/share/applications/moss.desktop"): #Remove old copy
        os.system("sudo rm /usr/share/applications/moss.desktop")
    if os.path.exists("local_app/dist"): #Remove old copy
        os.system("sudo rm -rf local_app/dist")
    if os.getcwd() == '/opt/LPF':
        os.system("cd local_app;sudo chmod a+x lpf_launch; sudo npm i; sudo ./node_modules/.bin/electron-rebuild;sudo npm run dist;sudo cp lpf.desktop /usr/share/applications/.; cd ..")
    else:
        os.system("cd local_app;sudo chmod a+x lpf_launch; npm i; ./node_modules/.bin/electron-rebuild; npm run dist;sudo cp lpf.desktop /usr/share/applications/.; cd ..")
    return True

def move_LPF_repo():
    cwd = os.getcwd()
    print("current working directory is {}".format(cwd))
    if (cwd != '/opt/LPF'):
        os.system("sudo rm -rf /opt/LPF")
        os.system("sudo cp -r {} /opt/LPF".format(cwd))
        os.system("sudo chmod a+rwx /opt/LPF")
def LPF_build_app():
    build_app()
    move_LPF_repo()
    check_dist_build()

def reinstall_app():
    if os.path.exists("/opt/LPF/local_app/dist"):
        os.system("sudo rm -rf local_app/dist")
    LPF_build_app()


def install_LPF_deps(user):
    if not check_kma():
        print("kma not found, installing")
        if os.path.exists("kma"):
            os.system("sudo rm -rf kma")
        os.system(
            "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma;make; sudo cp kma* /home/{}/bin/.; cd ..;".format(user))
    if not check_ccphylo():
        print("ccphylo not found, installing")
        if os.path.exists("ccphylo"):
            os.system("sudo rm -rf ccphylo")
        os.system(
            "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo; make; sudo cp ccphylo /home/{}/bin/.;  cd ..;".format(user))
    install_docker_images()
    if not check_google_chrome():
        os.system(
            "sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -nv; sudo apt install ./google-chrome-stable_current_amd64.deb; rm google*")
    #os.system("pip install -r requirements.txt")

def install_docker_images():
    docker_list = [
        "biocontainers/figtree:v1.4.4-3-deb_cv1",
        "staphb/quast:5.0.2",
        "nanozoo/bandage:0.8.1--7da3a06",
        "staphb/flye:2.9.1"
    ]
    for item in docker_list:
        cmd = "docker pull " + item
        os.system(cmd)

def install_ont_deps():
    os.system("sudo apt update")
    os.system("wget http://apt.zwets.it/debs/kcri-apt-repo_1.0.0_all.deb")
    os.system("sudo apt update")
    os.system("sudo apt install ./kcri-apt-repo_1.0.0_all.deb")
    os.system("sudo apt update")
    os.system("sudo apt install kcri-seqtz-repos")
    os.system("sudo apt update")
    os.system("wget http://apt.zwets.it/debs/kcri-seqtz-deps_1.3.0_amd64.deb")
    os.system("sudo apt install ./kcri-seqtz-deps_1.3.0_amd64.deb")
    os.system("sudo apt update")
    os.system('rm kcri-*')
    os.system('sudo groupadd docker; sudo usermod -aG docker $USER; sudo chmod 666 /var/run/docker.sock')

def solve_conda_env():
    proc = subprocess.Popen("conda env list", shell=True,
                            stdout=subprocess.PIPE, )
    env = proc.communicate()[0].decode().split()
    print("Checking for LPF environment")
    print(env)
    if 'LPF' in env:
        print("LPF environment already exists")
        print("Updating LPF environment")
        os.system("conda env update --file environment.yml  --prune")
    else:
        os.system("conda env create -f environment.yml")

def add_bin_path():
    infile = open(os.path.expanduser("~/.bashrc"), "r")
    data = infile.read()
    infile.close()
    data = data.split("\n")
    if "export PATH=$PATH:~/bin" not in data:
        print("Adding ~/bin to PATH")
        os.system("echo \'export PATH=$PATH:~/bin\' >> ~/.bashrc")
        os.system("source ~/.bashrc")
    print("Adding ~/bin to PATH")

def check_all_deps():
    os.system("cd /opt/LPF")
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
    approved = 0
    for item in check_list:
        if item == "ONT dependencies":
            if ont_check:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Docker images":
            if docker_images_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Pip dependencies":
            if pip_deps_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Google Chrome":
            if google_chrome_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(item + " is not installed")
        elif item == "Local App":
            if app_build_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Conda":
            if conda_result:
                print(bcolors.OKGREEN + item + " is installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Local software":
            if local_software_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
        elif item == "Local databases":
            if local_database_result:
                print(bcolors.OKGREEN + item + " are installed" + bcolors.ENDC)
                approved += 1
            else:
                print(bcolors.FAIL + item + " is not installed" + bcolors.ENDC)
    if len(check_list) == approved:
        print(bcolors.OKGREEN + "All dependencies are installed and LPF is ready for use." + bcolors.ENDC)
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
    if not os.path.exists('/opt/LPF_databases/resfinder_db/resfinder_db.name'):
        print(bcolors.FAIL + "Resfinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db.name'):
        print(bcolors.FAIL + "Plasmidfinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/LPF_databases/virulencefinder_db/virulencefinder_db.name'):
        print(bcolors.FAIL + "Virulencefinder database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/LPF_databases/mlst_db'):
        print(bcolors.FAIL + "MLST database not found" + bcolors.ENDC)
        return False
    if not os.path.exists('/opt/LPF_databases/bacteria_db/bacteria_db.name'):
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
        print("The following docker images are missing:")
        for item in docker_list:
            print(item)
        return False
    else:
        return True

def check_conda():
    home = str(Path.home())
    proc = subprocess.Popen("which conda", shell=True,
                            stdout=subprocess.PIPE, )
    conda_output = proc.communicate()[0].decode().rstrip()
    if (conda_output.startswith(home)):
        print(bcolors.OKGREEN + "Conda is installed corrently in /home/user/" + bcolors.ENDC)
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
    if 'LPF' in env:
        print(bcolors.OKGREEN + "LPF environment is installed" + bcolors.ENDC)
        return True
    else:
        print(bcolors.FAIL + "LPF environment is not installed" + bcolors.ENDC)
        return False

def check_app_build():
    path_list = ["/opt/LPF_data", "/opt/LPF_databases", "/opt/LPF_reports"]
    for item in path_list:
        if not os.path.exists(item):
            print(bcolors.FAIL+ item +" is not installed" + bcolors.ENDC)
            return False
    if check_dist_build():
        return True
    else:
        return False

def create_sql_db():
    print("Creating SQL database")
    conn = sqlite3.connect('/opt/LPF_databases/LPF.db')
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS sample_table(entry_id TEXT PRIMARY KEY, sample_type TEXT, reference_id TEXT)""")
    conn.commit()

    c.execute(
        """CREATE TABLE IF NOT EXISTS sequence_table(entry_id TEXT PRIMARY KEY, header TEXT, sequence TEXT)""")
    conn.commit()
    
    c.execute(
        """CREATE TABLE IF NOT EXISTS meta_data_table(entry_id TEXT PRIMARY KEY, meta_data_json TEXT)""") #Consider better design for meta_data
    conn.commit()

    c.execute(
        """CREATE TABLE IF NOT EXISTS status_table(entry_id TEXT PRIMARY KEY, input_file TEXT, status TEXT, time_stamp TEXT, stage TEXT)""")
    conn.commit()

    c.execute(
        """CREATE TABLE IF NOT EXISTS sync_table(last_sync TEXT, sync_round TEXT)""")
    conn.commit()
    conn.close()
    print("SQL database created")

def insert_bacteria_references_into_sql():
    sql_bacteria_reference_list = []
    bacteria_db_reference_list = []

    with open('/opt/LPF_databases/bacteria_db/bacteria_db.name', 'r') as f:
        for line in f:
            bacteria_db_reference_list.append(line.rstrip())

    if os.path.exists('/opt/LPF_databases/LPF.db'):
        result = sqlCommands.sql_fetch_all("SELECT header FROM sequence_table", '/opt/LPF_databases/LPF.db')
    else:
        sys.exit("LPF.db is not found")

    print("calculating the difference between the reference table and the database")
    local_missing_references_in_sql_db = set(set(bacteria_db_reference_list) - set(result))
    local_missing_references_in_bacteria_db = set(set(result) - set(bacteria_db_reference_list))

    if len(local_missing_references_in_sql_db) > 0:
        conn = sqlite3.connect('/opt/LPF_databases/LPF.db')
        print("Updating SQL database with new references. Number of new references: {}".format(len(local_missing_references_in_sql_db)))
        with open ('/opt/LPF_databases/bacteria_db/bacteria_db.name', 'r') as f:
            t = 0
            for line in f:
                t += 1
                if t%100 == 0:
                    print("{} references processed".format(t))
                if line.rstrip() in local_missing_references_in_sql_db: #set search
                    cmd = "~/bin/kma seq2fasta -t_db /opt/LPF_databases/bacteria_db/bacteria_db -seqs {}".format(t)
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = proc.communicate()[0].decode().rstrip()
                    reference_header_text = output.split("\n")[0][1:]
                    sequence = output.split("\n")[1]
                    entry_id = md5.md5_of_sequence(sequence)
                    cmd = 'INSERT OR IGNORE INTO sample_table VALUES ("{}", "{}", "{}")'.format(entry_id, 'bacteria', '')
                    sqlCommands.sql_execute_command(cmd, '/opt/LPF_databases/LPF.db')
                    cmd = 'INSERT OR IGNORE INTO sequence_table VALUES ("{}", "{}", "{}")'.format(entry_id, reference_header_text, '')
                    sqlCommands.sql_execute_command(cmd, '/opt/LPF_databases/LPF.db')
        conn.commit()
        conn.close()


def mkfs_LPF():
    """Makes the LPF filesystem"""
    path_list = ["/opt/LPF_data/",
                 "/opt/LPF_analyses/",
                 "/opt/LPF_metadata_json/",
                 "/opt/LPF_metadata_json/individual_json",
                 "/opt/LPF_databases/",
                 "/opt/LPF_reports/",
                 "/opt/LPF_logs/"]
    for item in path_list:
        if not os.path.exists(item):
            os.system("sudo mkdir -m 777 {}".format(item))
            print("Created {}".format(item))
            if item == '/opt/LPF_databases/':
                if os.path.exists('/opt/LPF_databases/LPF.db'):
                    os.system("sudo rm /opt/LPF_databases/LPF.db")
                    print("Removed old LPF.db")


def check_and_add_bookmarks():
    home = str(Path.home())
    if os.path.exists("{}/.config/gtk-3.0/bookmarks".format(home)):
        with open("{}/.config/gtk-3.0/bookmarks".format(home)) as fd:
            data = fd.readlines()
        new_bookmark_list = list()
        for item in data:
            if "LPF" not in item and "moss" not in item: #remove old moss bookmarks
                new_bookmark_list.append(item.rstrip())
        new_bookmark_list.append("file:///opt/LPF_data")
        new_bookmark_list.append("file:///opt/LPF_reports")
        new_bookmark_list.append("file:///opt/LPF_logs")
        new_bookmark_list.append("file:///opt/LPF_metadata_json")

        with open("{}/.config/gtk-3.0/bookmarks".format(home), 'w') as fd:
            for item in new_bookmark_list:
                fd.write(item + '\n')

def install_databases(arguments, cwd):
    print(arguments)
    """Installs the databases"""
    if not check_local_software:
        print(bcolors.FAIL + "LPF dependencies are not installed, and databases cant be indexed" + bcolors.ENDC)
        sys.exit()

    #database_list = ["resfinder_db",
    #                 "plasmidfinder_db",
    #                 "virulencefinder_db",
    #                 "bacteria_db"]
    database_list = []
    if arguments.bacteria_db != None:
        print('Copying bacteria database')
        if not os.path.exists('/opt/LPF_databases/bacteria_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/bacteria_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/bacteria_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/bacteria_db')
        for item in os.listdir(arguments.bacteria_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.bacteria_db, item), '/opt/LPF_databases/bacteria_db/bacteria_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.bacteria_db, item), '/opt/LPF_databases/bacteria_db/bacteria_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.bacteria_db, item), '/opt/LPF_databases/bacteria_db/bacteria_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.bacteria_db, item), '/opt/LPF_databases/bacteria_db/bacteria_db.comp.b'.format(item))
    else:
        database_list.append("bacteria_db")

    if arguments.resfinder_db != None:
        print('Copying resfinder database')
        if not os.path.exists('/opt/LPF_databases/resfinder_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/resfinder_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/resfinder_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/resfinder_db')
        for item in os.listdir(arguments.resfinder_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.resfinder_db, item), '/opt/LPF_databases/resfinder_db/resfinder_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.resfinder_db, item), '/opt/LPF_databases/resfinder_db/resfinder_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.resfinder_db, item), '/opt/LPF_databases/resfinder_db/resfinder_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.resfinder_db, item), '/opt/LPF_databases/resfinder_db/resfinder_db.comp.b'.format(item))
    else:
        database_list.append("resfinder_db")

    if arguments.plasmidfinder_db != None:
        print('Copying plasmidfinder database')
        if not os.path.exists('/opt/LPF_databases/plasmidfinder_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/plasmidfinder_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/plasmidfinder_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/plasmidfinder_db')
        for item in os.listdir(arguments.plasmidfinder_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.plasmidfinder_db, item), '/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.plasmidfinder_db, item), '/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.plasmidfinder_db, item), '/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.plasmidfinder_db, item), '/opt/LPF_databases/plasmidfinder_db/plasmidfinder_db.comp.b'.format(item))
    else:
        database_list.append("plasmidfinder_db")

    if arguments.virulencefinder_db != None:
        print('Copying virulencefinder database')
        if not os.path.exists('/opt/LPF_databases/virulencefinder_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/virulencefinder_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/virulencefinder_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/virulencefinder_db')
        for item in os.listdir(arguments.virulencefinder_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.virulencefinder_db, item), '/opt/LPF_databases/virulencefinder_db/virulencefinder_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.virulencefinder_db, item), '/opt/LPF_databases/virulencefinder_db/virulencefinder_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.virulencefinder_db, item), '/opt/LPF_databases/virulencefinder_db/virulencefinder_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.virulencefinder_db, item), '/opt/LPF_databases/virulencefinder_db/virulencefinder_db.comp.b'.format(item))
    else:
        database_list.append("virulencefinder_db")

    if arguments.cdd_db != None:
        print('Copying ccd database')
        if not os.path.exists('/opt/LPF_databases/cdd_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/cdd_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/cdd_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/cdd_db')
        for item in os.listdir(arguments.cdd_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.cdd_db, item), '/opt/LPF_databases/cdd_db/cdd_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.cdd_db, item), '/opt/LPF_databases/cdd_db/cdd_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.cdd_db, item), '/opt/LPF_databases/cdd_db/cdd_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.cdd_db, item), '/opt/LPF_databases/cdd_db/cdd_db.comp.b'.format(item))
    else:
        database_list.append("cdd_db")

    if arguments.virus_db != None:
        print('Copying virus database')
        if not os.path.exists('/opt/LPF_databases/virus_db'):
            os.system('sudo mkdir -m 777 /opt/LPF_databases/virus_db')
        else:
            os.system('sudo rm -r /opt/LPF_databases/virus_db')
            os.system('sudo mkdir -m 777 /opt/LPF_databases/virus_db')
        for item in os.listdir(arguments.virus_db):
            if item.endswith('.seq.b'):
                shutil.copyfile('{}/{}'.format(arguments.virus_db, item), '/opt/LPF_databases/virus_db/virus_db.seq.b'.format(item))
            elif item.endswith('.name'):
                shutil.copyfile('{}/{}'.format(arguments.virus_db, item), '/opt/LPF_databases/virus_db/virus_db.name'.format(item))
            elif item.endswith('.length.b'):
                shutil.copyfile('{}/{}'.format(arguments.virus_db, item), '/opt/LPF_databases/virus_db/virus_db.length.b'.format(item))
            elif item.endswith('.comp.b'):
                shutil.copyfile('{}/{}'.format(arguments.virus_db, item), '/opt/LPF_databases/virus_db/virus_db.comp.b'.format(item))
    else:
        database_list.append("virus_db")

    for item in database_list:
        if not os.path.exists('/opt/LPF_databases/{}'.format(item)):
            os.system("sudo mkdir -m 777 /opt/LPF_databases/{}".format(item))
        if not os.path.exists('/opt/LPF_databases/{}/{}.name'.format(item, item)):
            os.chdir('/opt/LPF_databases/{}'.format(item))
            os.system("sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/export/{0}.fasta.gz".format(item))
            if item == 'bacteria_db':
                os.system("kma index -i {}.fasta.gz -o {} -m 14 -Sparse ATG".format(item, item))
            else:
                os.system("kma index -i {}.fasta.gz -o {} -m 14".format(item, item))

    if arguments.mlst_db != None:
        os.chdir('/opt/LPF_databases')
        os.system("git clone https://bitbucket.org/genomicepidemiology/mlst_db.git")
        os.system('chmod -R 777 /opt/LPF_databases/mlst_db')
        os.chdir('/opt/LPF_databases/mlst_db')
        file_list = os.listdir('/opt/LPF_databases/mlst_db')
        for item in file_list:
            if os.path.exists('/opt/LPF_databases/mlst_db/{0}/{0}.fsa'.format(item)):
                os.chdir('/opt/LPF_databases/mlst_db/{}'.format(item))
                os.system("kma index -i {}.fsa -o {} -m 14".format(item, item))
                os.chdir('/opt/LPF_databases/mlst_db')
    else:
        if not os.path.exists('/opt/LPF_databases/mlst_db'):
            os.chdir('/opt/LPF_databases')
            os.system("git clone https://bitbucket.org/genomicepidemiology/mlst_db.git")
            os.system('chmod -R 777 /opt/LPF_databases/mlst_db')
            os.chdir('/opt/LPF_databases/mlst_db')
            file_list = os.listdir('/opt/LPF_databases/mlst_db')
            for item in file_list:
                if os.path.exists('/opt/LPF_databases/mlst_db/{0}/{0}.fsa'.format(item)):
                    os.chdir('/opt/LPF_databases/mlst_db/{}'.format(item))
                    os.system("kma index -i {}.fsa -o {} -m 14".format(item, item))
                    os.chdir('/opt/LPF_databases/mlst_db')

    os.chdir(cwd)
    os.system("cp scripts/schemes/notes.txt /opt/LPF_databases/virulencefinder_db/notes.txt")
    os.system("cp scripts/schemes/phenotypes.txt /opt/LPF_databases/resfinder_db/phenotypes.txt")
    if not os.path.exists('/opt/LPF_databases/cdd_db/cddid_all.tbl'):
        os.system('sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/cdd_db/export/cddid_all.tbl -O /opt/LPF_databases/cdd_db/cddid_all.tbl')

    if not os.path.exists('/opt/LPF_databases/LPF.db'):
        create_sql_db()
    elif os.path.getsize('/opt/LPF_databases/LPF.db') == 0:
        create_sql_db()
    insert_bacteria_references_into_sql()

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
            return True
    return False

def check_dist_build():
    local = False
    deployment = False
    if not os.path.isfile("local_app/dist/linux-unpacked/lpf"):
        print(bcolors.FAIL + "Local App is not installed in current working directory" + bcolors.ENDC)
        local = False
    else:
        print(bcolors.OKGREEN + "Local App is installed in current working directory" + bcolors.ENDC)
        local = True

    if not os.path.isfile("/opt/LPF/local_app/dist/linux-unpacked/lpf"):
        print(bcolors.FAIL + "Local App is not installed /opt/LPF" + bcolors.ENDC)
        deployment = False
    else:
        print(bcolors.OKGREEN + "Local App is installed /opt/LPF" + bcolors.ENDC)
        deployment = True
    if local and deployment:
        return True
    else:
        return False

def ci_install(user, cwd):
    """Installs the databases"""
    if not check_local_software:
        print(bcolors.FAIL + "LPF dependencies are not installed, and databases cant be indexed" + bcolors.ENDC)
        sys.exit()

    database_list = ["resfinder_db",
                     "plasmidfinder_db",
                     "virulencefinder_db",
                     "bacteria_db",
                     "cdd_db",
                     "virus_db"]

    for item in database_list:
        if not os.path.exists('/opt/LPF_databases/{}'.format(item)):
            os.system("sudo mkdir -m 777 /opt/LPF_databases/{}".format(item))
        if not os.path.exists('/opt/LPF_databases/{}/{}.name'.format(item, item)):
            os.chdir('/opt/LPF_databases/{}'.format(item))
            if item == 'bacteria_db':
                os.system('cp {}/tests/fixtures/database/* /opt/LPF_databases/bacteria_db/.'.format(cwd))
                os.system("kma index -i {}.fasta.gz -o {} -m 14 -Sparse ATG".format(item, item))
            else:
                os.system(
                    "sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/{0}/export/{0}.fasta.gz".format(
                        item))
                os.system("kma index -i {}.fasta.gz -o {} -m 14".format(item, item))

    if not os.path.exists('/opt/LPF_databases/mlst_db'):
        os.chdir('/opt/LPF_databases')
        os.system("git clone https://bitbucket.org/genomicepidemiology/mlst_db.git")
        os.system('chmod -R 777 /opt/LPF_databases/mlst_db')
        os.chdir('/opt/LPF_databases/mlst_db')
        file_list = os.listdir('/opt/LPF_databases/mlst_db')
        for item in file_list:
            if os.path.exists('/opt/LPF_databases/mlst_db/{0}/{0}.fsa'.format(item)):
                os.chdir('/opt/LPF_databases/mlst_db/{}'.format(item))
                os.system("kma index -i {}.fsa -o {} -m 14".format(item, item))
                os.chdir('/opt/LPF_databases/mlst_db')



    os.chdir(cwd)
    os.system("cp scripts/schemes/notes.txt /opt/LPF_databases/virulencefinder_db/notes.txt")
    os.system("cp scripts/schemes/phenotypes.txt /opt/LPF_databases/resfinder_db/phenotypes.txt")
    if not os.path.exists('/opt/LPF_databases/cdd_db/cddid_all.tbl'):
        os.system('sudo wget https://cge.food.dtu.dk/services/MINTyper/LPF_databases/cdd_db/export/cddid_all.tbl -O /opt/LPF_databases/cdd_db/cddid_all.tbl')
    if not os.path.exists('/opt/LPF_databases/LPF.db'):
        create_sql_db()
    elif os.path.getsize('/opt/LPF_databases/LPF.db') == 0:
        create_sql_db()
    insert_bacteria_references_into_sql()

    os.chdir(cwd)

    move_LPF_repo()


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


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, level):
       self.logger = logger
       self.level = level
       self.linebuf = ''

    def write(self, buf):
       for line in buf.rstrip().splitlines():
          self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass