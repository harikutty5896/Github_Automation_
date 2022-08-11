import json
import os
import GitOperation
import my_logger

get_file_list = []


class ChangeVersion:

    # JSON file loaded in constructor
    def __init__(self, json_path):
        my_logger.logger.info("----------------------------------------")
        self.json_path = json_path

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                my_logger.logger.info("Json File Opened Successfully")
                data = json.load(file)
                self.files_dict = self.load_json_to_dict(data)  # return dict

        except FileNotFoundError:
            my_logger.logger.error("FileNotFoundError Exception occurred", exc_info=True)
            msg = "Sorry, the file " + json_path + " does not exist."
            print(msg)

    # Load JSON file to Dict
    def load_json_to_dict(self, json_data):  # param data as string, ret dict
        file_dict = {}
        try:
            for path in json_data:
                prefix = GitOperation.file_path
                key = os.path.join(prefix, path)
                print("File Path :"+key + '\n')
                value = json_data[path]
                file_dict[key] = value
                my_logger.logger.info("{} filepath added to dict Successfully".format(key))
            return file_dict

        except AttributeError:
            my_logger.logger.error("AttributeError Exception occurred", exc_info=True)
            msg = "Attribute Error occurred !!"
            print(msg)

    # get line number for a field
    def get_line_number(self, data, field):  # optimize with map & return map with updated loc
        line_number = 0
        for line in data:
            line_number += 1
            if field in line:
                return line_number

    def get_build_line(self, field, value):
        if field == "FILEVERSION":
            return ' ' + field + ' ' + value + '\n'
        elif field == "FileVersion":
            return '            VALUE \"FileVersion\",' + ' ' + '\"' + value + '\"' + '\n'
        elif field == "PRODUCTVERSION":
            return ' ' + field + ' ' + value + '\n'
        elif field == "ProductVersion":
            return '            VALUE \"ProductVersion\",' + ' ' + '\"' + value + '\"' + '\n'

    def update_version(self, filename, version_number):
        comma_version_number = version_number.replace('.', ',')
        try:
            with open(filename, 'r', encoding='utf-8') as rc_file:
                data = rc_file.readlines()
                my_logger.logger.info("{} file opened".format(filename))

                # Finding Line number
                c_fv_line_number = self.get_line_number(data, "FILEVERSION")
                s_fv_line_number = self.get_line_number(data, "FileVersion")

                c_pv_line_number = self.get_line_number(data, "PRODUCTVERSION")
                s_pv_line_number = self.get_line_number(data, "ProductVersion")

                # Changing File Version
                data[c_fv_line_number - 1] = self.get_build_line("FILEVERSION", str(comma_version_number))
                data[s_fv_line_number - 1] = self.get_build_line("FileVersion", version_number)

                # Changing Product Version
                data[c_pv_line_number - 1] = self.get_build_line("PRODUCTVERSION", str(comma_version_number))
                data[s_pv_line_number - 1] = self.get_build_line("ProductVersion", version_number)

            with open(filename, 'w', encoding='utf-8') as rc_file:
                rc_file.writelines(data)
                my_logger.logger.info("Version edited successfully")
                suff = os.path.basename(filename)
                print(suff + ": Successfully Edited")
                return 1

        except FileNotFoundError:
            my_logger.logger.error("File not exist in the directory")
            return 0

    # From Dict, we replace the version to file
    def replace_version(self):
        try:
            for key, value in self.files_dict.items():
                if bool(self.update_version(key, value)):
                    # Append file name for commit
                    get_file_list.append(key)
                    my_logger.logger.info("{} added to list for commit".format(key))
                    print("\n{} added to list for commit\n".format(key))
                else:
                    print("File not added for commit")
        except:
            print("Exception Occurred")
            my_logger.logger.error("Exception occurred while changing version in .rc file", exc_info=True)

# new method - update-version(filename, version)
