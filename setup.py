import  os
#cmd = "sudo apt-get install build-essential"
#os.system(cmd)
#Kma
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
cmd = "pip install posix-ipc"
os.system(cmd)

####DOCKER:IMAGES: UNICYCLER

#Now, Install Docker VIA: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
#docker pull nanozoo/unicycler
