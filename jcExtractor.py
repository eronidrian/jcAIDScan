import csv
import os
import subprocess
from os import path
import re

SCRIPT_VERSION = '0.2.1'
BASE_PATH = '.'

lines = []

jc_version = "310"


def add_line(line: list[str]):
    if line not in lines:
        lines.append(line)

def parse_signature(signature: str) -> str:
    match = re.search(r"(\(.*\))", signature)
    signature = match.group(1)

    signature = re.sub(r'\[B', "byte[];", signature)
    signature = re.sub(r'\[S', "short[];", signature)
    signature = re.sub(r'\[Z', "boolean[];", signature)
    signature = re.sub(r'\[I', "int[];", signature)

    signature = re.sub(f'SS', "short;short;", signature)
    signature = re.sub(f'BB', "byte;byte;", signature)
    signature = re.sub(f'II', "int;int;", signature)
    signature = re.sub(f'([ISBZ;(])I', r'\1int;', signature)
    signature = re.sub(f'([ISBZ;(])S', r'\1short;', signature)
    signature = re.sub(r'([ISBZ;(])B', r'\1byte;', signature)
    signature = re.sub(r'([ISBZ;(])Z', r'\1boolean;', signature)

    signature = re.sub(r'\(L', "(", signature)
    signature = re.sub(r';L', ";", signature)
    signature = re.sub("/", ".", signature)

    signature = re.sub(r';\)', ")", signature)

    return signature


def export_lines():
    csv_file = open(f"overview_table_{jc_version}.csv", 'w', newline='')
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(["AID", "package name", "class token", "class name", "method token", "method name", "method signature"])

    for i in range(len(lines) - 1):
        if not set(lines[i]).issubset(set(lines[i + 1])):
            if len(lines[i]) == 7:
                lines[i][6] = parse_signature(lines[i][6])
            csv_writer.writerow(lines[i])


def print_info():
    print(
        "jcExtractor v{0} tool for extracting the AIDs of JavaCard packages and their class details."
        "\nCheck https://github.com/petrs/jcAIDScan/ for the newest version and documentation.\n2018, Petr Svenda\n."
        " For extraction of the information, please put the intended Java Card Kit folder"
        " in current directory. Also ensure that Java Card Kit folder has api_export_files sub-directory".format(
            SCRIPT_VERSION))


def main():
    export_files = []
    package_name = []

    print_info()

    # kit_directory = input('Enter Java Card Kit Directory Name (Please ensure the folder is in current directory: ')
    # java_os = input('Java OS Version(E.g. 2.2.2): ')
    kit_directory = f'jc{jc_version}_kit'
    classdir = "-classdir " + path.join(kit_directory,"api_export_files")
    # exptool = kit_directory+"\\bin\\exp2text"

    # Here we find the exp files in recursive directory search
    # Then capture the package name using the path found and stored in package_name list
    # Convert the exp files in text files using Java Card Kit built-in application called exp2text
    # The path for all converted text files is stored in export_files list
    for root, dirs, files in os.walk(path.join(BASE_PATH, kit_directory, "api_export_files")):
        for file in files:
            if file.endswith('.exp'):
                export_file_path = path.join(root, file)
                path1 = export_file_path.split("api_export_files" + path.sep, 1)[1]
                filename = file.split(".exp", 1)[0]
                path_details = path1.split(path.sep)
                package = ''
                for subpath in path_details:
                    package = package + subpath
                    if subpath == filename:
                        break
                    else:
                        package = package + '.'
                print(package)
                package_name.append(package)


                # Run exp2text program and create a text file of export files.
                exp2text = "./exp2text_new " + classdir + " " + package
                result = subprocess.call(exp2text, stdout=subprocess.PIPE, shell=True)
                if result != 0:
                    print("Extraction failed")
                    return
                else:
                    export_text_path = path.join(root, filename) + "_exp.tex"
                    export_files.append(export_text_path)

    # Check whether the conversion of exp files to text file was successful or not
    for entry in export_files:
        if not os.path.exists(entry):
            print("Extraction Failed\n")
            return
        else:
            print(entry)

    # Till this point, we have all the package names and text files of each export files
    # In exp file, package related information is found in Constant_Package_info section
    # and Class related information found in class_info section
    search = ["CONSTANT_Package_info", "class_info", "method_info"]

    # f1 = open(path.join(BASE_PATH, java_os + "_package_details.txt"),
    #           'w')  # This file stores the information about the packages
    # f1.write("FULL AID:OS VER:AID:PACKAGE NAME\n")

    export_file_index = -1  # This variable is used to keep track of the location in export_files list

    # Each export file is searched for package and class details. Every exp file has package information first
    #  and then class information

    for entry in export_files:
        export_file_index = export_file_index + 1
        # open the text file of export file
        f = open(entry, 'r')
        file_content = f.read().splitlines()

        index = -1  # This variable is used to keep track of the location last read from text file

        # Search for Package information first
        for line_item in file_content:
            index = index + 1
            if search[0] in line_item:
                break  # Package information is found. Index is noted.
            else:
                continue

        # Extract package information like Minor version, Major Version, aid_length and aid from subsequent lines
        minor_text = file_content[index + 4]
        minor_version = minor_text.split("minor_version\t", 1)[1]
        major_text = file_content[index + 5]
        major_version = major_text.split("major_version\t", 1)[1]

        aid_len_detail = file_content[index + 6]
        aid_length = aid_len_detail.split("aid_length\t", 1)[1]
        aid_detail = file_content[index + 7]
        aid_strings = aid_detail.split("aid\t", 1)[1]
        if len(minor_version) < 2:
            minor_version = "0" + minor_version
        if len(major_version) < 2:
            major_version = "0" + major_version
        if len(aid_length) < 2:
            aid_length = "0" + aid_length
        aid_indl_strings = aid_strings.split(':')
        aid = ""
        for substrings in aid_indl_strings:
            temp = substrings.split("0x", 1)[1]
            if len(temp) < 2:
                temp = "0" + temp
            aid = aid + temp
        full_aid = minor_version + major_version + aid_length + aid

        print(minor_version + major_version + aid_length + aid)

        # The package information is stored in file
        # f1.write(full_aid + ":" + java_os + ":" + aid + ":" + package_name[export_file_index] + "\n")

        # Now searching for Class Info
        # Create a file in class_files with the name of the full package aid
        # f2 = open(path.join(BASE_PATH, "class_files", full_aid), 'w')

        # Search the remaining exp from the previous index value
        # This way each exp file is search from top to bottom only once
        for line_item in file_content[index:]:
            if search[1] in line_item:

                # Class info entry found
                # Extract class name and token id and populate the class files in format <Classname>:<tokenid>

                class_full_name = file_content[index].split("// ", 1)[1]
                class_strings = class_full_name.split('/')
                class_name = class_strings[len(class_strings) - 1]

                # Now extract Token No
                class_token_no = file_content[index + 1].split("token\t", 1)[1]
                # f2.write(class_name + ":" + class_token_no + "\n")

                index = index + 1
                method_index = index
                # Now find the method details from current index no.
                # f3 = open(path.join(BASE_PATH, "method_files", "{0}_{1}.txt".format(full_aid, class_token_no)), 'w')
                for line_item1 in file_content[method_index:]:
                    if search[1] in line_item1:
                        # f3.close()
                        break
                    if search[2] in line_item1:  # Method Info structure found
                        method_token_no = file_content[method_index + 1].split("token\t", 1)[1]
                        # if all(["static" not in file_content[method_index + 2],
                        #         "abstract" not in file_content[method_index + 2]]):
                        #     method_index = method_index + 1
                        #     continue
                        # else:
                        #     if "static" in file_content[method_index + 2]:
                        #         method_type = "static"
                        #     else:
                        #         method_type = "abstract"
                        method_name = file_content[method_index + 3].split("// ", 1)[1]
                        method_signature = file_content[method_index + 4].split("// ", 1)[1]
                        # f3.write(method_name + ":" + method_token_no + ":" + method_type + "\n")
                        if method_name != 'equals' and method_name != '<init>':
                            add_line([aid, package_name[export_file_index], class_token_no, class_name, method_token_no, method_name, method_signature])
                        method_index = method_index + 1
                    else:
                        add_line([aid, package_name[export_file_index], class_token_no, class_name])
                        method_index = method_index + 1
                # f3.close()
            else:
                add_line([aid, package_name[export_file_index]])
                index = index + 1
                continue
        # f2.close()
    # f1.close()
    export_lines()
    return


if __name__ == "__main__":
    main()
