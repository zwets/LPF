import js2py
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-assembly', action="store_true", type=bool, default=False, dest="assembly")
    parser.add_argument('-alignment', action="store_true", type=bool, default=False, dest="alignment")')

    args = parser.parse_args()
    eval_res, js_file = js2py.run_file("createPDF.js")
    js_file.generatePDFReport(args.target_dir)

def generate_assembly_report(bacterial_parser):
    eval_res, js_file = js2py.run_file("createPDF.js") #to run the js file
    js_file.generatePDFReport(bacterial_parser.data.target_dir) #bacterial_parser.data.target_dir is the id to call the function
