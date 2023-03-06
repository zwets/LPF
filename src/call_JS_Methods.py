import os
import sys
import datetime
import dataframe_image as dfi
import pandas as pd
import js2py

def generate_pdf_report(bacterial_parser):

    eval_res, js_file = js2py.run_file("createPDF.js") #to run the js file
    js_file.generatePDFReport(bacterial_parser.data.target_dir) #bacterial_parser.data.target_dir is the id to call the function
#def generate_alignment_report(bacterial_parser):
#    eval_res, js_file = js2py.run_file("createPDF.js")
#    js_file.generateAlignmentReportPDF(bacterial_parser.data.target_dir)
