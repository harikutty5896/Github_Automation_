import os.path
import sys
import time
import git
from git import Repo
import json
import my_logger
from datetime import datetime


class GitOperation:
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
        self.updated_file_path = ''
        try:
            with open(self.git_json_path, 'r', encoding='utf-8') as git_json_file:
                self.json_file_data = json.load(git_json_file)
                my_logger.logger.info("Git data json file opened successfully")

                # After read and store the lines in json_file_data load and parse has to happen in constructor
                self.git_json_dict = self.git_load_json_to_map(self.json_file_data)  # load json to dict
                self.parse_data_from_dict()

                # if clone_path is not specified creating directory in script folder
                if not (self.git_clone_path.strip()):
                    my_logger.logger.info("Given path is empty in json file")
                    print("Given clone path is empty\n")

                    self.updated_file_path = os.path.join(self.path, "Repository")
                    self.git_clone_path = self.updated_file_path

                else:
                    self.updated_file_path = self.git_clone_path

                # if directory exist creates new directory with timestamp
                self.isdir_exist = os.path.isdir(self.updated_file_path)
                if self.isdir_exist:
                    milliseconds = int(round(time.time() * 1000))
                    self.git_clone_path = self.git_clone_path + '_' + str(milliseconds)

                    my_logger.logger.info("Creating new directory with timestamp")
                    print("\nCreating new directory with timestamp\n")

                    self.updated_file_path = self.git_clone_path

        except FileNotFoundError:
            my_logger.logger.error("Error in opening git json file")
            my_logger.logger.error("Exception occurred in Git operation constructor", exc_info=True)

    def git_load_json_to_map(self, json_data):
        temp_dict = {}
        try:

            for item in json_data:
                value = json_data[item]
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

    def add_files_for_commit(self, source_list):
        for key in source_list:
            self.files_list.append(key)
            self.repo.git.add(key)

        changedFiles = [item.a_path for item in self.repo.index.diff('Head')]
        if changedFiles:
            print("Below files are Modified:")
            for files in changedFiles:
                print(files)

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
            my_logger.logger.info("Commit Message :" + msg)

        except:
            my_logger.logger.error("Error occurred in commit_files()", exc_info=True)

    def git_push(self, files_list):
        try:
            self.add_files_for_commit(files_list)
            self.commit_files()
            try:
                origin = self.repo.remote(name='origin')
                origin.pull()  # how to resolve conflict?

                if bool(origin.push()):
                    print("\n\nUpdated and Pushed successfully")
                    my_logger.logger.info("Updated and Pushed successfully")
                else:
                    print("\n\nPush FAILED")
                    my_logger.logger.info("Push FAILED", exc_info=True)
            except:
                print("Error in git_push()")
                my_logger.logger.error("Error in git_push()", exc_info=True)

        except:
            my_logger.logger.error("Error in git_push() method while adding files for commit", exc_info=True)
            print("Error in git_push()")

    def git_clone(self):
        try:

            r = Repo.clone_from(self.git_repo_url, self.git_clone_path)
            r.git.checkout(self.branch)

            my_logger.logger.info("Github repository cloned successfully")
            print("Github repository cloned successfully\n")

            # after parsing the data and directory is created
            self.repo = Repo(self.git_clone_path)

        except:
            my_logger.logger.error("Error in git_pull().May be Given directory already contain .git folder",
                                   exc_info=True)
            print("Error in git_pull()")
            print("Exiting..")
            sys.exit()

    def __del__(self):
        git_repo = git.Repo(self.updated_file_path)
        git_repo.close()

    def get_file_path(self):
        return self.updated_file_path
