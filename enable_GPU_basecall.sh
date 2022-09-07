#!/bin/bash

# use ONT config_editor to ensure correct linking of guppy binaries to minknow
sudo /opt/ont/minknow/bin/config_editor --conf application \
  --filename /opt/ont/minknow/conf/app_conf \
  --set guppy.server_executable="/opt/ont/guppy/bin/guppy_basecall_server" \
  --set guppy.client_executable="/opt/ont/guppy/bin/guppy_basecall_client" \
  --set guppy.gpu_calling=1 \
  --set guppy.num_threads=16 \
  --set guppy.ipc_threads=2


## 7.
# restart the minknow.service after making modifications
sudo systemctl restart minknow.service


## 8.
# create the guppyd.service at the correct location
sudo tee -a /lib/systemd/system/guppyd.service >/dev/null <<<'[Unit]
Description=Service to manage the guppy basecall server.
Documentation=https://community.nanoporetech.com/protocols/Guppy-protocol/v/GPB_2003_v1_revQ_14Dec2018
[Service]
Type=simple
ExecStart=/opt/ont/guppy/bin/guppy_basecall_server --log_path /var/log/guppy --config dna_r9.4.1_450bps_fast.cfg --port 5555 -x cuda:all
Restart=always
User=root
MemoryLimit=8G
MemoryHigh=8G
CPUQuota=200%
[Install]
Alias=guppyd.service
WantedBy=multi-user.target'


## 9.
# enable guppyd.service to start/load automatically
sudo systemctl enable guppyd.service
# restart the guppyd.service after making modifications
sudo systemctl restart guppyd.service

# completed
echo -e "... installation and setup finished ..."

##/END