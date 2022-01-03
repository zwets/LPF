import  os
#./node_modules/.bin/electron-rebuild #Run this always
#cmd = "sudo apt-get install build-essential"
#os.system(cmd)
#Kma

def main():
    #Ret til python3 -m
    #Assumes anaconda is installed
    #Assumes manual installation of cuda  https://developer.nvidia.com/cuda-downloads
    #Manual docker installation and enable

    """
    For ubuntu 20.04:
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
    sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/11.4.2/local_installers/cuda-repo-ubuntu2004-11-4-local_11.4.2-470.57.02-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2004-11-4-local_11.4.2-470.57.02-1_amd64.deb
    sudo apt-key add /var/cuda-repo-ubuntu2004-11-4-local/7fa2af80.pub
    sudo apt-get update
    sudo apt-get -y install cuda

    For guppy:
    sudo apt-get update
    sudo apt-get install wget lsb-release
    export PLATFORM=$(lsb_release -cs)
    wget -O- https://mirror.oxfordnanoportal.com/apt/ont-repo.pub | sudo apt-key add -
    echo "deb http://mirror.oxfordnanoportal.com/apt ${PLATFORM}-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
    sudo apt-get update
    sudo apt update
    sudo apt install ont-guppy


    """
    print("Sudo is required for apt update")
    cmd = "sudo apt update"
    os.system(cmd)
    cmd = "sudo apt-get install libz-dev"
    os.system(cmd)
    cmd = "sudo apt  install curl"
    os.system(cmd)
    cmd = "sudo apt-get install r-base"
    os.system(cmd)
    cmd = "curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -"
    os.system(cmd)
    cmd = "sudo apt install nodejs"
    os.system(cmd)
    cmd = "sudo apt install npm; npm install mkdirp"
    os.system(cmd)
    print("Installing KMA")
    cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma; git checkout nano; make; cd ..;"
    os.system(cmd)
    print("Installing CCphylo")
    cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
    os.system(cmd)
    cmd = "sudo apt install python3-pip"
    os.system(cmd)
    findersinstall()
    cmd = "python3 -m pip install fpdf"
    os.system(cmd)
    cmd = "pip install geocoder; pip install pandas"
    os.system(cmd)
    cmd = "pip install geopy"
    os.system(cmd)
    cmd = "pip install Nominatim"
    os.system(cmd)
    print("Installing docker")
    cmd = "sudo apt install docker.io; sudo systemctl enable --now docker; sudo usermod -a -G docker $USER;"
    os.system(cmd)
    cmd = "Rscript r_packages_install.R"
    os.system(cmd)



def findersinstall():
    cmd = "python3 -m pip install tabulate biopython cgecore gitpython python-dateutil"
    os.system(cmd)
    cmd = "git clone https://bitbucket.org/genomicepidemiology/mlst.git; cd mlst; git checkout nanopore; git clone https://bitbucket.org/genomicepidemiology/mlst_db.git; cd mlst_db; git checkout nanopore; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
    os.system(cmd)
    cmd = "git clone https://git@bitbucket.org/genomicepidemiology/resfinder.git; cd resfinder; git checkout nanopore_flag; git clone https://git@bitbucket.org/genomicepidemiology/resfinder_db.git db_resfinder; cd db_resfinder; git checkout minimizer_implementation; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git db_pointfinder; cd db_pointfinder; python3 INSTALL.py ../../kma/kma_index non_interactive; cd ..; cd ..;"
    os.system(cmd)
    cmd = "git clone https://bitbucket.org/genomicepidemiology/plasmidfinder.git; cd plasmidfinder; git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git; cd plasmidfinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
    os.system(cmd)
    cmd = "git clone https://bitbucket.org/genomicepidemiology/virulencefinder.git; cd virulencefinder; git clone https://bitbucket.org/genomicepidemiology/virulencefinder_db.git; cd virulencefinder_db; python3 INSTALL.py ../../kma/kma_index; cd ..; cd ..;"
    os.system(cmd)



#Docker install missing

if __name__ == '__main__':
    main()