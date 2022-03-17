import os
import sys
import subprocess

def main():
    check_anaconda()
    docker_check()
    check_nvidia()
    #Check OS dependencies
        #Nvidia-smi
    #Check and install non pip dependencies
    #Check and install pip dependencies
    #Move everything to generic location such as /usr/etc/etc ?
    #Create generic stored place for each initialized system. Make
    #Install KMA and other stuff? CCphylo?
    #create executable in bin
    return True

def check_nvidia():
    cmd = "nvidia-smi"
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode().rstrip()
    print (output)



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