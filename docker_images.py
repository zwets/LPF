import os
import sys
cmd = "docker pull biocontainers/figtree:v1.4.4-3-deb_cv1;\
    docker pull nanozoo/unicycler:0.4.7-0--c0404e6;\
    docker pull staphb/quast;\
    docker pull genomicpariscentre/guppy-gpu;\
    docker pull ontresearch/medaka"
os.system(cmd)