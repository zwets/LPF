import os

os.system('sudo groupadd docker; sudo usermod -aG docker $USER; su -s ${USER}; newgrp docker;')
print ('Please restart the terminal and confirm the docker installation my running the docker images command and check for no errors')