import json
import os
import my_logger


class ChangeVersion:

    # JSON file loaded in constructor
    def __init__(self, json_path, local_rep_name_prefix):
        my_logger.logger.info("----------------------------------------")
        self.json_path = json_path
        self.local_rep_prefix = local_rep_name_prefix
        self.files_to_commit = []

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                my_logger.logger.info("Json File Opened Successfully")
                data = json.load(file)
                self.files_dict = self.load_json_to_dict(data)

        except FileNotFoundError:
            my_logger.logger.error("FileNotFoundError Exception occurred", exc_info=True)
            msg = "Sorry, the file " + json_path + " does not exist."
            print(msg)

    # Load JSON file to Dict
    def load_json_to_dict(self, json_data):
        file_dict = {}
        try:
            for path in json_data:
                prefix = self.local_rep_prefix
                key = os.path.join(prefix, path)

                print("File Path :" + key + '\n')

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

    def get_newly_built_line_for_key(self, key, value):
        if key == "FILEVERSION":
            return ' ' + key + ' ' + value + '\n'
        elif key == "FileVersion":
            return '            VALUE \"FileVersion\",' + ' ' + '\"' + value + '\"' + '\n'
        elif key == "PRODUCTVERSION":
            return ' ' + key + ' ' + value + '\n'
        elif key == "ProductVersion":
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
                data[c_fv_line_number - 1] = self.get_newly_built_line_for_key("FILEVERSION", str(comma_version_number))
                data[s_fv_line_number - 1] = self.get_newly_built_line_for_key("FileVersion", version_number)

                # Changing Product Version
                data[c_pv_line_number - 1] = self.get_newly_built_line_for_key("PRODUCTVERSION",
                                                                               str(comma_version_number))
                data[s_pv_line_number - 1] = self.get_newly_built_line_for_key("ProductVersion", version_number)

            with open(filename, 'w', encoding='utf-8') as rc_file:
                rc_file.writelines(data)

                my_logger.logger.info("Version edited successfully")
                print(os.path.basename(filename) + ": Successfully Edited")

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
                    self.files_to_commit.append(key)

                    my_logger.logger.info("{} added to list for commit".format(key))
                    print("\n{} added to list for commit\n".format(key))

                else:
                    print("File not added for commit")
        except:
            print("Exception Occurred")
            my_logger.logger.error("Exception occurred while changing version in .rc file", exc_info=True)

    def get_files_to_commit(self):
        return self.files_to_commit
