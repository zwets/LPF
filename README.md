Read more about Microbial Outbreak Surveillance System here:
> PUBLICATION TBA

# Table of contents
Installation:
Clone from github; run setup.py; run docker_images.py; cd local_app && npm install;

Start app from local_app directory with "npm start" command.

nvidia-smi
nvcc -version
nvcc --version
sudo apt install nvidia-cuda-toolkit
reboot

nvidia-smi
sudo apt install nvidia-utils-460
nvidia-smi
ls
sudo prime-select query
dkms status
grep nvidia /etc/modprobe.d/* /lib/modprobe.d/*
rm -rf /etc/modprobe.d/blacklist-framebuffer.conf:blacklist
sudo update-initramfs -u
reboot

nvidia-smi
sudo dkms remove nvidia/460.39 --all
sudo dkms install nvidia/460.39 -k $(uname -r)
sudo update-initramfs -u
sudo dkms remove nvidia/460.39 --all
sudo dkms install --force nvidia/460.39 -k $(uname -r)
sudo update-initramfs -u
sync

reboot


nvidia-smi
sudo apt-get remove --purge '^nvidia-.*'
sudo nvidia-uninstall
ubuntu-drivers devices
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo ubuntu-drivers autoinstall
sudo reboot

nvidia-smi
nvcc --version
sudo apt install nvidia-cuda-toolkit
nvcc --version
nvidia-smi
ls
sudo ubuntu-drivers autoinstall
sudo reboot
