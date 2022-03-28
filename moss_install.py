import os
import sys
import subprocess

def main():
    check_anaconda()
    docker_check()
    check_nvidia()
    if not os.path.exists("/opt/ont/minknow/"):
        sys.exit("MinKNOW is not installed in /opt/ont/minknow/ . Please locate the installation here, as it should be by default.")
    os.system("pip install -r requirements.txt")
    install_apt_dependencies()
    #Check APT dependencies
    os.system("git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..")
    os.system("git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;")

    # Moving repo to /usr/etc
    os.system("cd ..; sudo mv moss /opt/moss")

    #Make solution for finders

    #Move everything to generic location such as /usr/etc/etc ?

    #Create generic stored place for each initialized system. Make
    #Install KMA and other stuff? CCphylo?
    #create executable in bin
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
    os.system("wget https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_6.0.1_linux64.tar.gz; tar –xvzf ont-guppy_6.0.1_linux64.tar.gz")

    return True

def install_apt_dependencies():
    apt_list = ["sudo apt update",
                "sudo apt-get install libz-dev",
                "sudo apt  install curl",
                "sudo apt install nodejs",
                "sudo apt install npm",
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
    if name_check and version_check:
        return True
    else:
        sys.exit("Please install a version of anaconda that is atleast 1.7 or newer")


if __name__ == '__main__':
    main()