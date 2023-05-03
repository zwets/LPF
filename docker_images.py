import os
docker_list = [
    "biocontainers/figtree:v1.4.4-3-deb_cv1",
    "staphb/quast:5.0.2",
    "nanozoo/bandage:0.8.1--7da3a06",
    "docker pull staphb/prokka:1.14.6"
]
for item in docker_list:
    cmd = "docker pull " + item
    os.system(cmd)