import os
import sys

os.system('sudo rm -rf /etc/apt/sources.list.d/kcri*')
os.system('sudo rm -rf /etc/apt/sources.list.d/ont*')
os.system('sudo rm -rf /opt/ont')
os.system('sudo apt remove minknow*')
os.system('sudo apt remove ont-*')
os.system('sudo apt remove nodejs')
os.system('sudo apt purge kcri*')
os.system('sudo rm /etc/symtemd/system/guppy*')
os.system('sudo rm /etc/symtemd/system/minknow*')
os.system('sudo rm /etc/symtemd/system/multi-user.target.wants/guppy*')
os.system('sudo rm /etc/symtemd/system/multi-user.target.wants/minknow*')