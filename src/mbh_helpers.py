# Copyright (c) 2021, Malte Bjørn Hallgren Technical University of Denmark
# All rights reserved.
# This is a helper function library for generic tasks.

#Import Libraries
import sys
import os

def print_to_logfile(input, logfilem, stdout):
    print (input, file=logfile)
    if stdout:
        print (input)
