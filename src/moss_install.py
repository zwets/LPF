import os
import sys
#Install kma
print ("Sudo is required for apt update")
cmd = "sudo apt update"
os.system(cmd)
#print ("Sudo is required to install libz-dev")
cmd = "sudo apt-get install libz-dev"
os.system(cmd)
print ("Installing KMA")
cmd = "git clone https://bitbucket.org/genomicepidemiology/kma.git; cd kma && make; cd ..;"
os.system(cmd)
print ("Installing CCphylo")
cmd = "git clone https://bitbucket.org/genomicepidemiology/ccphylo.git; cd ccphylo && make; cd ..;"
os.system(cmd)
cmd = "pip install posix-ipc; "
os.system(cmd)


print ("Installing docker")
cmd = "sudo apt install docker.io; sudo systemctl enable --now docker; sudo usermod -a -G docker $USER; newgrp docker;"
os.system(cmd)