import shutil
import os
import subprocess
from shutil import copyfile
import time
import textwrap

SCRIPT_VERSION = '0.1.1'
BASE_PATH = '.'

export_files=[]
package_name=[]
class_name=[]


def print_info():
    print("jcExtractor v{0} tool for extracting the AIDs of JavaCard packages and their class details.\nCheck https://github.com/petrs/jcAIDScan/ "
          "for the newest version and documentation.\n2018, Petr Svenda\n. For extraction of the information, please put the intended Java Card Kit folder"
          " in current directory. Also ensure that Java Card Kit folder has api_export_files sub-directory".format(SCRIPT_VERSION))


def main():
    print_info()
    kit_directory= input('Enter Java Card Kit Directory Name (Please ensure the folder is in current directory: ')
    java_os = input ('Java OS Version(E.g. 2.2.2: ')
    classdir = "-classdir "+kit_directory+"\\api_export_files"
    # exptool = kit_directory+"\\bin\\exp2text"

    # Here we find the exp files in recursive directory search
    # Then capture the package name using the path found and stored in package_name list
    # Convert the exp files in text files using Java Card Kit built-in application called exp2text
    # The path for all converted text files is stored in export_files list
    for root, dirs, files in os.walk("{0}\\{1}\\api_export_files".format(BASE_PATH,kit_directory)):
        for file in files:
            if file.endswith('.exp'):
                export_file_path='{0}\\{1}'.format(root,file)
                path1=export_file_path.split("api_export_files\\",1)[1]
                filename=file.split(".exp",1)[0]
                path_details = path1.split("\\")
                package=''
                for subpath in path_details:
                    package=package + subpath
                    if subpath == filename:
                        break
                    else:
                        package=package + '.'
                print(package)
                package_name.append(package)

                # Run exp2text program and create a text file of export files.
                exp2text="exp2text " + classdir + " " +package
                result= subprocess.call(exp2text, stdout=subprocess.PIPE, shell=True)
                if result != 0:
                    print("Extraction failed")
                    return
                else:
                    export_text_path=root+"\\"+filename+"_exp.tex"
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
    search = ["CONSTANT_Package_info","class_info"]

    f1 = open(BASE_PATH + "\\{0}".format(java_os + "_package_details.txt"), 'w') #This file stores the information about the packages
    f1.write("FULL AID:OS VER:AID:PACKAGE NAME\n")

    export_file_index = -1 #This variable is used to keep track of the location in export_files list

    # Each export file is searched for package and class details. Every exp file has package information first and then class information

    for entry in export_files:
        export_file_index=export_file_index+1
        # open the text file of export file
        f=open(entry,'r')
        file_content=f.read().splitlines()

        index=-1 # This variable is used to keep track of the location last read from text file

        # Search for Package information first
        for line_item in file_content:
            index=index+1
            if search[0] in line_item:
                break; #Package information is found. Index is noted.
            else:
                continue

        # Extract package information like Minor version, Major Version, aid_length and aid from subsequent lines
        minor_text=file_content[index+4]
        minor_version=minor_text.split("minor_version\t",1)[1]
        major_text=file_content[index+5]
        major_version = major_text.split("major_version\t", 1)[1]

        aid_len_detail=file_content[index+6]
        aid_length=aid_len_detail.split("aid_length\t", 1)[1]
        aid_detail=file_content[index+7]
        aid_strings = aid_detail.split("aid\t", 1)[1]
        if len(minor_version)< 2:
            minor_version="0"+minor_version
        if len(major_version)< 2:
            major_version="0"+major_version
        if len(aid_length) < 2:
            aid_length = "0" + aid_length
        aid_indl_strings=aid_strings.split(':')
        aid=""
        for substrings in aid_indl_strings:
            temp=substrings.split("0x",1)[1]
            if len(temp) < 2:
                temp="0"+temp
            aid=aid+temp
        full_aid=minor_version+major_version+aid_length+aid

        print(minor_version+major_version+aid_length+aid)

        # The package information is stored in file
        f1.write(full_aid+":"+java_os+":"+aid+":"+package_name[export_file_index]+"\n")

        # Now searching for Class Info
        # Create a file in class_files with the name of the full package aid
        f2 = open(BASE_PATH+"\\class_files\\{0}.txt".format(full_aid),'w')

        # Search the remaining exp from the previous index value
        # This way each exp file is search from top to bottom only once
        for line_item in file_content[index:]:
            if search[1] in line_item:

                # Class info entry found
                # Extract class name and token id and populate the class files in format <Classname>:<tokenid>

                class_full_name=file_content[index].split("// ",1)[1]
                class_strings=class_full_name.split('/')
                class_name=class_strings[len(class_strings)-1]

                # Now extract Token No
                token_no= file_content[index+1].split("token\t",1)[1]
                f2.write(class_name+":"+token_no+"\n")
                index = index + 1
            else:
                index = index + 1
                continue
        f2.close()
    f1.close()
    return

if __name__ == "__main__":
    main()