import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser(description='.')
parser.add_argument("-light", action="store_true", default = False, dest="light", help="Does not download CGE databases and GUPPY for basecalling.")
args = parser.parse_args()

def main(args):
    os.system("sudo apt install npm; sudo apt install git;")
    if args.light:
        os.system("cd /opt/moss; git pull")
        cwd = os.getcwd()
    else:
        cwd = os.getcwd()
    check_anaconda()
    docker_check()
    check_nvidia()
    if not os.path.exists("/opt/ont/minknow/"):
        sys.exit("MinKNOW is not installed in /opt/ont/minknow/ . Please locate the installation here, as it should be by default.")
    os.system("pip install -r requirements.txt")
    install_apt_dependencies()
    os.system("git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; make; cd ..")
    os.system("git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;")
    #Check APT dependencies

    # Moving repo to /usr/etc
    if cwd != "/opt/moss":
        move_moss_repo(cwd)
    install_app()

    if not args.light:
        cmd = "cd /opt/moss; git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py /opt/moss/kma/kma_index; cd ..; cd ..;"
        os.system(cmd)
        guppy_installer()

    path_list = ["/opt/moss_db", "/opt/moss_data/", "/opt/moss_data/fast5/", "/opt/moss_data/fastq/"]
    for item in path_list:
        if not os.path.exists(item):
            os.system("sudo mkdir -m 777 {}".format(item))

    #Make solution for finders
    download_finder_dbs() #Check if works TBD

    os.system("python3 /opt/moss/docker_images.py")


    #Create generic stored place for each initialized system. Make
    #Install KMA and other stuff? CCphylo?
    #create executable in bin

    #Update the guppy-worklist on updates? or reinstalls

    check_dist_build()
    return True

def check_dist_build():
    if not os.path.isdir("/opt/moss/local_app/dist/"):
        sys.exit("A MOSS distribution was not created correctly. Installation was not completed")

def download_finder_dbs():
    os.system("git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git")
    os.system("git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git resfinder_db")
    os.system("git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git")
    os.system("/opt/moss/kma/kma_index -i /opt/moss/plasmidfinder_db/*.fsa -o /opt/moss/plasmidfinder_db/all")
    os.system("/opt/moss/kma/kma_index -i /opt/moss/resfinder_db/*.fsa -o /opt/moss/resfinder_db/all")
    os.system("/opt/moss/kma/kma_index -i /opt/moss/virulencefinder_db/*.fsa -o /opt/moss/virulencefinder_db/all")

def install_app():
    os.system("cd /opt/moss/local_app; chmod a+x moss_launch; npm i; ./node_modules/.bin/electron-rebuild; npm run dist;sudo cp moss.desktop /usr/share/applications/.")
    return True

def move_moss_repo(cwd):
    # Make moss start shortcut in bin
    if os.path.exists("/opt/moss"):
        os.system("sudo rm -rf /opt/moss")
        os.system("sudo mv {} /opt/moss".format(cwd))
    else:
        os.system("sudo mv {} /opt/moss".format(cwd))
    return True

def move_shortcut_script():
    # Make moss start shortcut in bin
    if os.path.exists("~/bin/"):
        os.system("chmod a+x /opt/moss/moss; sudo mv /opt/moss/moss ~/bin/moss")
    else:
        os.system("sudo mkdir ~/bin/")
        os.system("chmod a+x /opt/moss/moss; sudo mv /opt/moss/moss ~/bin/moss")
    return True

def guppy_installer():
    os.system("wget https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_6.0.7_linux64.tar.gz --no-check-certificate")
    os.system("tar -xvf ont-guppy_6.0.7_linux64.tar.gz")

    return True

def install_apt_dependencies():
    apt_list = ["sudo apt update",
                "sudo apt-get install libz-dev",
                "sudo apt  install curl",
                #"curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -; sudo apt-get install -y nodejs"
                "sudo apt update; sudo apt install nodejs",
                "sudo npm install -g npm@latest",
                "npm install mkdirp",
                "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb; sudo apt install ./google-chrome-stable_current_amd64.deb; rm google*"]
    print("Sudo is required for apt update")
    for item in apt_list:
        os.system(item)
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