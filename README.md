pip install websockets
pip install paramiko
pip install scp 






Read more about MinION-Typer here:
> PUBLICATION TBA

# Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Background](#background)
* [Pipelines](#pipelines)
    * [Research](#research)
    * [Append](#append)
    * [Surveillance](#surveillance)
* [Options and usage](#options-and-usage)
    * [Functions](#functions)
    * [Standard usage](#standard-options)
# Introduction

MinION-Typer is a tool designed for quick and precise typing of bacterial isolates. 
MinION-Typer has a series of pipelines that can be utilized depending on whether or not the user would like to type and determine phylogeny in a research related capacity, or if the user would like to use the build-in surveillance function to build a SQL-database for pathogenic outbreak discovery.


# Requirements

* Linux or macOS
* [Python](https://www.python.org/) 3.4 or later
* [Anaconda3](https://www.anaconda.com/distribution/) As new as possible, but most should work
* [Unicycler](https://github.com/rrwick/Unicycler) Unicycler has a lot of dependencies (Spades, Racon, Bowtie2 etc.), so make sure that these are all installed correctly for Unicycler to run.
* [KMA](https://bitbucket.org/genomicepidemiology/kma) As new as possible, but most should work
* [ccphylo](https://bitbucket.org/genomicepidemiology/ccphylo/src/master/) As new as possible, but most should work


# Installation
The following instructions will install the latest version of MinION-Typer:
* If not install already, install Python, Anaconda3 and Spades from the links above. 
* Clone the MinION-Typer repository and install MinIon-Typer from:
```bash
git clone git@github.com:s153002/ndtree.git
python3 MinIon-Typer_install.py
rm MinIon-Typer_install.py
```
* Install KMA from:
```bash
git clone https://bitbucket.org/genomicepidemiology/kma.git
cd kma && make
mv kma ~/bin/
cd ..
```
* Install ccphylo from:
```bash
git clone https://bitbucket.org/genomicepidemiology/ccphylo.git
cd ccphylo && make
ccphylo ~/bin/
cd ..
```

# Background

# Pipelines
MinION-Typer consists of 3 pipelines: Research, Append and Surveillance.

### Research

The research pipeline produces a distance matrix and a phylogenetic tree of a set of isolates. The pipeline takes an input consisting of the input samples,
a reference database and optional conditions for data processing. Unless a custom template is given (-ref), the best template will be calculated from the reference data base (-db) (The best template is defined as the template that scores highest on average across all given input samples).
A KMA mapping of the input reads to the best template is done, and the found consensus sequences are processed according to the options stated when the program was called (Prune, dcmMethylation, etc.).
A pair-wise calculation is done to produce the distance matrix from the processed consensus sequences, and the distance matrix is then convert to a newick format for visual representation of the phylogenetic tree.


### Append

Currently disabled (Not working)

### Surveillance

Currently disabled due to implementation of UniCycler

#Options and usage

## Functions
### Research-Pipeline
The Research pipeline has the following functions that may be called from the commandline:

* -i_path_illumina /// (Complete path to the directory containing all the Illumina samples you would like to analyze)
* -i_path_nanopore /// (Complete path to the directory containing all the Nanopore samples you would to analyze)
* -pe /// (If you are using paired-end illumina files, please use this condition)
* -dcmMethylation /// (dcmMethylation removes dcm methylation motifs found in the sequence. These motifs are CCXGG, and the most common input to the function in "N" which includes all base combinations of the motif.)
* -prune /// (The Prune function removes SNPs that are located too close to each other. If SNP_1 and SNP_2 are located within X distance of each other, the frame of SNP_1-X to SNP_2+X are removed)
* -prune_distance /// (Possibility of defining your own distance for pruning)
* -bc /// (For Nanopore KMA mapping you can give your own value for base calling)
* -db /// (Complete path to your reference Database)
* -thread /// (Number of threads to be used for KMA mapping)
* -ref /// (Single Reference to be used instead of a reference database.)
* -o_path /// (Custom output directory path. Should only be used in rare cases, otherwise default output in the current working directory)
* -o /// (Name of the output directory)

The Append pipeline has the following functions that may be called from the commandline:

* -i_path_illumina /// (Complete path to the directory containing all the Illumina samples you would like to analyze)
* -i_path_nanopore /// (Complete path to the directory containing all the Nanopore samples you would to analyze)
* -pe /// (If you are using paired-end illumina files, please use this condition)
* -o_path /// (Custom output directory path. Should only be used in rare cases, otherwise default output in the current working directory)
* -o /// (Name of the output directory)

The Surveillance pipeline has the following functions that may be called from the commandline:

* -i_illumina /// (Complete path to the single input illumina file or two paired-end files)
* -i_nanopore /// (Complete path to the single input nanopore file)
* -pe /// (If you are using paired-end illumina files, please use this condition)
* -dcmMethylation /// (dcmMethylation removes dcm methylation motifs found in the sequence. These motifs are CCXGG, and the most common input to the function in "N" which includes all base combinations of the motif.)
* -prune /// (The Prune function removes SNPs that are located too close to each other. If SNP_1 and SNP_2 are located within X distance of each other, the frame of SNP_1-X to SNP_2+X are removed)
* -prune_distance /// (Possibility of defining your own distance for pruning)
* -bc /// (For Nanopore KMA mapping you can give your own value for base calling)
* -ref_kma_db /// (Complete path to the reference database you generated whilst running MinION_initializer.py)
* -isolate_db /// (Complete path to the isolate database you generated whilst running MinION_initializer.py)
* -isolate_storage /// (Complete path to the isolate storage directory you generated whilst running MinION_initializer.py)
* -reference_storage ///(Complete path to the reference storage directory you generated whilst running MinION_initializer.py)
* -o_path /// (Custom output directory path. Should only be used in rare cases, otherwise default output in the current working directory)
* -o /// (Name of the output directory)

 
### Standard usage

Make sure to index your reference database with "kma index -Sparse ATG" to make the reference finding faster!

An example of using the reference pipeline:
MinION-Typer research -i_path_illumina /home/user/illumina_reads/ -i_path_nanopore /home/user/nanopore_reads/ -dcmMethylation N -prune -db /home/user/database/bacteria_database.ATG -o output








