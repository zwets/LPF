import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser(description='.')
parser.add_argument("-action", action="store_true", default = False, dest="action", help="github action")
args = parser.parse_args()

def main(args):
    if not os.path.exists('~/bin/'):
        os.system('sudo mkdir ~/bin/')
    copy_install_files()
    os.system('sudo apt-get update && apt-get upgrade')
    os.system('sudo apt-get install kcri-seqtz-deps')
    os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -nv; sudo apt install ./google-chrome-stable_current_amd64.deb; rm google*")
    os.system("pip install -r requirements.txt")


def copy_install_files():
    os.system("sudo cp install_files/kcri-seqtz.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/nanoporetech.sources.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/nodesource.list /etc/apt/sources.list.d/.")
    os.system("sudo cp install_files/cran_ubuntu_key.asc /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/mozillateam-ubuntu-ppa.gpg /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/nodesource.gpg /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/ont-repo.asc /etc/apt/trusted.gpg.d/.")
    os.system("sudo cp install_files/mozilla-ppa /etc/apt/preferences.d/.")

if __name__ == '__main__':
    main(args)