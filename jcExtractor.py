import csv
import os
import subprocess
from os import path
import re

from api_specification.api_specification import ApiSpecification

BASE_PATH = '.'

def main():

    version = "visa"
    dirname = f"jc{version}_kit"
    export_files = []
    for root, dirs, files in os.walk(path.join(BASE_PATH, dirname, "api_export_files")):
        for file in files:
            if file.endswith('_exp.tex'):
                export_file_path = path.join(root, file)
                export_files.append(export_file_path)

    specification = ApiSpecification.load_from_export_files(export_files)
    specification.export_to_csv(f"overview_table_{version}_new.csv")


if __name__ == "__main__":
    main()
