import os
import sys
import subprocess
import argparse
import time

parser = argparse.ArgumentParser(description='.')
parser.add_argument("-action", action="store_true", default = False, dest="action", help="github action")
parser.add_argument("-pab", action="store_true", default = False, dest="pab", help="pull and build app")
args = parser.parse_args()

def main(args):
    if not os.path.exists('~/bin'):
        os.system('sudo mkdir ~/bin')
    time.sleep(3)
    if args.pab:
        os.system('cd /opt/moss; git pull;')

        #install_app()
        #check_dist_build()
        #return True
    elif args.action: #Github tests
        cwd = os.getcwd()
        os.system(
            "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -nv; sudo apt install ./google-chrome-stable_current_amd64.deb; rm google*")
        os.system("pip install -r requirements.txt")
        os.system("git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; make; sudo cp kma* ~/bin/.; cd ..; mv kma src/.;")
        os.system("git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; sudo cp ccphylo ~/bin/.;  cd ..; mv ccphylo src/.;")
        os.system("git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py ~/bin/kma_index;")
        download_finder_dbs()

        install_app()
        path_list = ["/opt/moss_db", "/opt/moss_data/", "/opt/moss_data/fast5/", "/opt/moss_data/fastq/"]
        for item in path_list:
            if not os.path.exists(item):
                os.system("sudo mkdir -m 777 {}".format(item))
        #os.system("python3 docker_images.py")
        check_dist_build()
        if cwd != "/opt/moss":
            move_moss_repo(cwd)
        return True
    else: #Main install pulls everything except anaconda3
        #check_anaconda() #Write check to check that ~/anaconda3/bin/conda exists
        cwd = os.getcwd()
        copy_install_files()
        os.system('sudo apt-get update && sudo apt-get upgrade')
        os.system('sudo apt-get install kcri-seqtz-deps')
        os.system('sudo groupadd docker; sudo usermod -aG docker $USER; sudo chmod 666 /var/run/docker.sock')
        os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -nv; sudo apt install ./google-chrome-stable_current_amd64.deb; rm google*")
        os.system("pip install -r requirements.txt")
        os.system(
            "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; make; sudo cp kma* ~/bin/.; cd ..; mv kma src/.;")
        os.system(
            "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; sudo cp ccphylo ~/bin/.;  cd ..; mv ccphylo src/.;")
        os.system("git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py ~/bin/kma_index;")
        install_app()
        path_list = ["/opt/moss_db", "/opt/moss_data/", "/opt/moss_data/fast5/", "/opt/moss_data/fastq/"]
        for item in path_list:
            if not os.path.exists(item):
                os.system("sudo mkdir -m 777 {}".format(item))
        download_finder_dbs()
        os.system("python3 docker_images.py")
        check_dist_build()
        cmd = "python3 src/create_guppy_workflow_dict.py"
        os.system(cmd)
        if cwd != "/opt/moss":
            move_moss_repo(cwd)
        return True

def copy_install_files():
    os.system("sudo cp install_files/kcri-seqtz.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/nanoporetech.sources.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/nodesource.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/cran_ubuntu_key.asc /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/mozillateam-ubuntu-ppa.gpg /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/nodesource.gpg /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/ont-repo.asc /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/mozilla-ppa /etc/apt/preferences.d/.")

def check_dist_build():
    if not os.path.isfile("local_app/dist/linux-unpacked/moss"):
        sys.exit("A MOSS distribution was not created correctly. Installation was not completed")
    else:
        print ("The installation was completed")

def download_finder_dbs():
    os.system("git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git")
    os.system("git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git resfinder_db")
    os.system("git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git")
    os.system("~/bin/kma_index -i plasmidfinder_db/*.fsa -o plasmidfinder_db/all")
    os.system("~/bin/kma_index -i resfinder_db/*.fsa -o resfinder_db/all")
    os.system("~/bin/kma_index -i virulencefinder_db/*.fsa -o virulencefinder_db/all")

def install_app():
    os.system("cd local_app; chmod a+x moss_launch; npm i; ./node_modules/.bin/electron-rebuild; npm run dist;sudo cp moss.desktop /usr/share/applications/.; cd ..")
    return True

def move_moss_repo(cwd):
    # Make moss start shortcut in bin
    if os.path.exists("/opt/moss"):
        os.system("sudo rm -rf /opt/moss")
        os.system("sudo mv {} /opt/moss".format(cwd))
    else:
        os.system("sudo cp -r {} /opt/moss".format(cwd))
    return True

def guppy_installer():
    os.system("wget https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_6.0.7_linux64.tar.gz --no-check-certificate")
    os.system("tar -xvf ont-guppy_6.0.7_linux64.tar.gz")

    return True

def check_pip_dependencies():
    return True

def check_nvidia():
    cmd = "nvidia-smi"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    var_list = ["NVIDIA-SMI", "Driver Version:", "CUDA Version:", "Processes:"]
    if all(x in output for x in var_list):
        return True
    else:
        print (output)
        sys.exit("NVIDIA Tool kit not properly installed.")



def docker_check():
    cmd = "docker --version"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    name_check = "Docker version"
    if output.startswith(name_check):
        name_check = True
    #Version doesn't really matter that much. Perhaps change later is needed.

    cmd = "docker images"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    if output == "":
        sys.exit("Docker is not installed.")
    docker_check = "REPOSITORY"
    if output.split("\n")[0].startswith(docker_check):
        docker_check = True
    else:
        print (output)
        sys.exit("Docker has not been installed correctly. See the error msg above.")

    if docker_check and name_check:
        return True
    else:
        sys.exit("Docker as not been installed correctly")



def check_anaconda():
    cmd = "anaconda -V"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    if output == "":
        sys.exit("Anaconda is not installed.")
    name_check = "anaconda Command line client"
    version_check = "1.7.0" #Require 1.7 or newer
    if output.startswith(name_check):
        name_check = True
    version = output.split()[-1][:-1]
    if version > version_check:
        version_check = True
    #Copy to /bin/
    cmd = "which conda"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    print ("sudo cp {} /bin/.".format(output))
    os.system("sudo cp {} /bin/.".format(output))

    cmd = "conda env list"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    if "base" not in output:
        os.system("conda create --name base")

    if name_check and version_check:
        return True
    else:
        sys.exit("Please install a version of anaconda that is atleast 1.7 or newer")


if __name__ == '__main__':
    main(args)