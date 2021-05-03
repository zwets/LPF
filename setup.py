import  os
#cmd = "sudo apt-get install build-essential"
#os.system(cmd)
#Kma

def main():
    cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git"
    os.system(cmd)
    cmd = "cd kma && make"
    os.system(cmd)
    cmd = "cd .."
    os.system(cmd)
    #ccphylo
    cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git"
    os.system(cmd)
    cmd = "cd ccphylo && make"
    os.system(cmd)
    cmd = "cd .."
    os.system(cmd)
    cmd = "sudo apt install python3-pip"
    os.system(cmd)
    cmd = "pip install posix-ipc"
    os.system(cmd)

def installresfinder():
    cmd = "python3 -m pip install tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder.git; cd resfinder; cd cge; git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma && make; cd ..; wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.1/ncbi-blast-2.10.1+-x64-linux.tar.gz; tar zxvpf ncbi-blast-2.10.1+-x64-linux.tar.gz; cd ..;"
    os.system(cmd)
    cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git db_resfinder; cd db_resfinder; python3 INSTALL.py ../../kma non_interactive; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git db_pointfinder; cd db_pointfinder; python3 INSTALL.py ../../kma non_interactive; cd .."
    os.system(cmd)

####DOCKER:IMAGES: UNICYCLER

#Now, Install Docker VIA: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
#docker pull nanozoo/unicycler


if __name__ == '__main__':
    main()