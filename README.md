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
