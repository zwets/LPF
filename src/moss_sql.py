# Copyright (c) 2019, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
#

#Import Libraries
import sys
import os
import argparse
import operator
import time
import geocoder
import gc
import numpy as np
import array
import subprocess
import threading
from optparse import OptionParser
from operator import itemgetter
import re
import json
import sqlite3
import json
import datetime
import hashlib
import gzip

import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import gzip
from fpdf import FPDF
from pandas.plotting import table
from geopy.geocoders import Nominatim
from subprocess import check_output, STDOUT

def sql_edit(config_name, string):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    c.execute(string)
    conn.commit()
    conn.close()

def sql_fetch(string, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    c.execute(string)
    data = c.fetchall()
    conn.close()
    return data


def insert_consensus_name(entry_id, config_name, consensus_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    entry_id_statement = "entry_id = '{}'".format(entry_id)

    dbstring = "UPDATE sample_table SET consensus_name = '{}' WHERE {}".format(consensus_name, entry_id_statement)
    print (dbstring)
    c.execute(dbstring)

    conn.commit()
    conn.close()

def insert_metadata_table(entry_id, entries, values, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()

    dbstring = "INSERT INTO metadata_table(entry_id, {}) VALUES('{}', {})".format(entries, entry_id.replace("'", "''"), values)

    c.execute(dbstring)

    conn.commit()
    conn.close()

def update_reference_table(entry_id, amrgenes, virulencegenes, plasmids, reference_header_text, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    amrgenes_statement = "amrgenes = '{}'".format(amrgenes)
    virulencegenes_statement = "virulencegenes = '{}'".format(virulencegenes)
    plasmids_statement = "plasmids = '{}'".format(plasmids)
    if amrgenes != None:
        dbstring = "UPDATE reference_table SET {} WHERE reference_header_text = '{}'".format(amrgenes_statement, reference_header_text)
        c.execute(dbstring)
    if virulencegenes != None:
        dbstring = "UPDATE reference_table SET {} WHERE reference_header_text = '{}'".format(virulencegenes_statement, reference_header_text)
        c.execute(dbstring)
    if plasmids != None:
        dbstring = "UPDATE reference_table SET {} WHERE reference_header_text = '{}'".format(plasmids_statement, reference_header_text)
        c.execute(dbstring)

    conn.commit()
    conn.close()

def insert_amr_table(entry_id, sample_name, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning, config_name):

    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()


    dbstring = "INSERT INTO amr_table(entry_id, sample_name, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
        .format(entry_id, sample_name, analysistimestamp, amrgenes, phenotypes, specie, risklevel, warning)
    c.execute(dbstring)

    conn.commit()
    conn.close()

def init_status_table(entry_id, status, type, current_stage, final_stage, result, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()

    dbstring = "INSERT INTO status_table(entry_id, status, type, current_stage, final_stage, result) VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(
        entry_id, status, type, current_stage, final_stage, result)
    c.execute(dbstring)
    conn.commit()
    conn.close()

def update_status_table(entry_id, status, type, current_stage, final_stage, result, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    entry_id_statement = "entry_id = '{}'".format(entry_id)
    status_statement = "status = '{}'".format(status)
    type_statement = "type = '{}'".format(type)
    current_stage_statement = "current_stage = '{}'".format(current_stage)
    final_stage_statement = "final_stage = '{}'".format(final_stage)
    result_statement = "result = '{}'".format(result)
    time_statement = "time_stamp = '{}'".format(str(datetime.datetime.now())[0:-7])

    dbstring = "UPDATE status_table SET {}, {}, {}, {}, {}, {} WHERE {}".format(status_statement, type_statement, current_stage_statement, final_stage_statement, result_statement, time_statement, entry_id_statement)
    c.execute(dbstring)

    conn.commit()
    conn.close()

def init_sample_table(entry_id, reference_header_text, sample_name, plasmid_string, allresgenes, virulence_string, config_name, referenceid):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    dbstring = "INSERT INTO sample_table(entry_id, reference_header_text, sample_name, analysistimestamp, plasmids, amrgenes, virulencegenes, referenceid) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
        entry_id, reference_header_text, sample_name, str(datetime.datetime.now())[0:-7], plasmid_string.replace("'", "''"),
        allresgenes.replace(", ", ",").replace("'", "''"), virulence_string.replace("'", "''"), referenceid)

    c.execute(dbstring)
    conn.commit()
    conn.close()

def update_sample_table(entry_id, reference_header_text, sample_name, plasmid_string, allresgenes, virulence_string, config_name):
    conn = sqlite3.connect("/opt/moss_db/{}/moss.db".format(config_name))
    c = conn.cursor()
    entry_id_statement = "entry_id = '{}'".format(entry_id)
    reference_header_text_statement = "reference_header_text = '{}'".format(reference_header_text)
    sample_name_statement = "sample_name = '{}'".format(sample_name)
    plasmid_string_statement = "plasmids = '{}'".format(plasmid_string)
    allresgenes_statement = "amrgenes = '{}'".format(allresgenes)
    virulence_string_statement = "virulencegenes = '{}'".format(virulence_string)

    dbstring = "UPDATE sample_table SET {}, {}, {}, {}, {} WHERE {}".format(reference_header_text_statement, sample_name_statement, plasmid_string_statement, allresgenes_statement, virulence_string_statement, entry_id_statement)
    c.execute(dbstring)

    conn.commit()
    conn.close()