import os.path
import sys
import time
from git import Repo
import json
import my_logger
import subprocess
import ChangeVersion
from datetime import datetime

file_path = ''


class GitOperation():
    def __init__(self, gjson_path):
        self.repo = None
        my_logger.logger.info("----------------------------------------")
        self.isdir_exist = None
        self.git_json_path = gjson_path
        self.git_access_token = ""
        self.git_repo_url = ""
        self.git_clone_path = ""
        self.files_list = []
        self.path = os.getcwd()
        self.branch = "master"
        try:
            with open(self.git_json_path, 'r', encoding='utf-8') as git_json_file:
                self.json_file_data = json.load(git_json_file)
                my_logger.logger.info("Git data json file opened successfully")

                # After read and store the lines in json_file_data load and parse has to happen in constructor
                self.git_json_dict = self.git_load_json_to_map()  # load json to dict
                self.parse_data_from_dict()

                global file_path
                # if clone_path is not specified creating directory in script folder
                if not (self.git_clone_path.strip()):
                    my_logger.logger.info("Given path is empty in json file")
                    print("Given clone path is empty")
                    file_path = os.path.join(self.path, "Repository")
                    self.git_clone_path = file_path
                else:
                    file_path = self.git_clone_path

                # if directory exist creates new directory with timestamp
                self.isdir_exist = os.path.isdir(file_path)
                if self.isdir_exist:
                    milliseconds = int(round(time.time() * 1000))
                    self.git_clone_path = self.git_clone_path + '_' + str(milliseconds)
                    my_logger.logger.info("Creating new directory with timestamp")
                    print("Creating new directory with timestamp")
                    file_path = self.git_clone_path

        except FileNotFoundError:
            my_logger.logger.error("Error in opening git json file")
            my_logger.logger.error("Exception occurred in Git operation constructor", exc_info=True)

    def git_load_json_to_map(self):
        temp_dict = {}
        try:
            for item in self.json_file_data:
                value = self.json_file_data[item]
                temp_dict[item] = value
                my_logger.logger.info("{} added to dict Successfully".format(item))
        except AttributeError:
            my_logger.logger.error("AttributeError Exception occurred", exc_info=True)
            msg = "Attribute Error occurred while loading data from json to dict !!"
            print(msg)
        return temp_dict

    def parse_data_from_dict(self):
        try:
            self.git_access_token = self.git_json_dict['access_token']
            self.git_clone_path = (self.git_json_dict['clone_path']).strip()
            self.git_repo_url = (self.git_json_dict['repo_url']).strip()
            self.branch = self.git_json_dict['branch_name']

            my_logger.logger.info("Successfully parsed data from dict")

        except KeyError:
            my_logger.logger.error("KeyError Exception occurred in parse_data_from_dict() - JSON Format is wrong",
                                   exc_info=True)
            msg = "Exception occurred in parse_data_from_dict()"
            print(msg)

    def add_files_for_commit(self):
        source_list = ChangeVersion.get_file_list  # it must contain files which has modified
        for key in source_list:
            self.files_list.append(key)
            self.repo.git.add(key)
        subprocess.run(["git", "status"], cwd=self.git_clone_path)

    def commit_files(self):
        try:
            now = datetime.now()
            time_ = now.strftime("%d/%m/%Y %H:%M:%S")

            files_string = ""
            for file in self.files_list:
                f_name = os.path.basename(file)
                files_string += f_name + ", "

            msg = 'Commit from VersionUpdater on ' + time_ + ' Files: ' + files_string
            self.repo.index.commit(msg)
            # subprocess.run(["git", "show"], cwd=self.git_clone_path)
            # above line show changed line and previous line

        except:
            my_logger.logger.error("Error occurred in commit_files()", exc_info=True)

    def git_push(self):
        try:
            self.add_files_for_commit()
            self.commit_files()
            try:
                origin = self.repo.remote(name='origin')
                if bool(origin.push()):
                    print("\n\nUpdated and Pushed successfully")
                    my_logger.logger.info("Updated and Pushed successfully")

            except:
                print("Error in git_push()")
                my_logger.logger.error("Error in git_push()", exc_info=True)

        except:
            my_logger.logger.error("Error in git_push() method while adding files for commit", exc_info=True)
            print("Error in git_push()")

    def git_pull(self):
        try:
            if not self.isdir_exist:
                print("Directory not exist ..Creating new Directory")
                my_logger.logger.info("Directory not exist ..Creating new Directory")
            else:
                print("Directory Exist.Creating new directory with timestamp")
                my_logger.logger.info("Directory Exist.Deleting and creating this directory again")

            Repo.clone_from(self.git_repo_url, self.git_clone_path)
            subprocess.run(["git", "switch", self.branch], cwd=self.git_clone_path)

            my_logger.logger.info("Github repository cloned successfully")
            print("Github repository cloned successfully")

            # after parsing the data and directory is created
            self.repo = Repo(self.git_clone_path)

        except:
            my_logger.logger.error("Error in git_pull().May be Given directory already contain .git folder",
                                   exc_info=True)
            print("Error in git_pull()")
            print("Exiting..")
            sys.exit()

    def __del__(self):
        print("Destructor of GitOperation")
        Repo.__del__(self)