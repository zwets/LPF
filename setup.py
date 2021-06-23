import  os
#cmd = "sudo apt-get install build-essential"
#os.system(cmd)
#Kma

def main():
    #Ret til python3 -m
    #Assumes anaconda is installed
    print("Sudo is required for apt update")
    cmd = "sudo apt update"
    os.system(cmd)
    cmd = "sudo apt-get install libz-dev"
    os.system(cmd)
    cmd = "sudo apt  install curl"
    os.system(cmd)
    cmd = "curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -"
    os.system(cmd)
    cmd = "sudo apt install nodejs"
    os.system(cmd)
    print("Installing KMA")
    cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma && make; cd ..;"
    os.system(cmd)
    print("Installing CCphylo")
    cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
    os.system(cmd)
    cmd = "sudo apt install python3-pip"
    os.system(cmd)
    findersinstall()
    cmd = "pip install posix-ipc"
    os.system(cmd)
    cmd = "pip install fpdf"
    os.system(cmd)
    print("Installing docker")
    cmd = "sudo apt install docker.io; sudo systemctl enable --now docker; sudo usermod -a -G docker $USER;"
    os.system(cmd)
    cmd = "newgrp docker"
    os.system(cmd)


def findersinstall():
    cmd = "python3 -m pip install tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder.git; cd resfinder; cd cge; git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma && make; cd ..; wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.1/ncbi-blast-2.10.1+-x64-linux.tar.gz; tar zxvpf ncbi-blast-2.10.1+-x64-linux.tar.gz; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git db_resfinder; cd db_resfinder; python3 INSTALL.py ../../kma non_interactive; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git db_pointfinder; cd db_pointfinder; python3 INSTALL.py ../../kma non_interactive; cd ..; cd ..;"
    os.system(cmd)
    cmd = "git clone https://bitbucket.org/genomicepidemiology/plasmidfinder.git; cd plasmidfinder; git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git; cd plasmidfinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
    os.system(cmd)
    cmd = "git clone https://bitbucket.org/genomicepidemiology/virulencefinder.git; cd virulencefinder; git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git; cd virulencefinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
    os.system(cmd)


#Docker install missing

if __name__ == '__main__':
    main()