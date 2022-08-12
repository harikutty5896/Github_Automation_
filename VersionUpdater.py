import time
from git import rmtree
import ChangeVersion
import my_logger
import json
import os
from colorama import init, Fore
from GitOperation import GitOperation

init(convert=True)  # For Console color


def check_files():
    if os.path.exists('file_config.json') and os.path.exists('git_config.json'):
        return True
    else:
        print("JSON Configured file Missing in current directory")
        my_logger.logger.error("JSON Configured file Missing in current directory")
        return False


def create_sample():
    git_config = {
        "repo_url": " your_repo_link ",
        "clone_path": " your_local_directory ",
        "access_token": " ",
        "branch_name": " "
    }
    file_config = {
        "filename.txt": "9.0.9.0",
        "filename_2.txt": "9.0.9.0"
    }
    json_object_1 = json.dumps(git_config, indent=4)
    json_object_2 = json.dumps(file_config, indent=2)

    with open('git_config.json', 'w') as file:
        file.write(json_object_1)
        print("Sample Git Config created Successfully")

    with open('file_config.json', 'w') as file:
        file.write(json_object_2)
        print("Sample file Config created Successfully")


def del_directory(d_path):
    rmtree(d_path)
    print("Directory deleted successfully")
    my_logger.logger.info("Directory deleted successfully")


if __name__ == '__main__':
    dpath = ''
    print(Fore.CYAN + 'VERSION UPDATER')
    print("===================================================\n")
    print("You must have to configure JSON file (git_config , file_config) in this directory \n"
          "Make sure to check both file in current directory\n")
    print("===================================================")
    print("MENU")
    print("1.Generate Sample JSON File Format")
    print("2.Run Version Update Process\n")

    try:
        choice = int(input("Enter your choice : "))
        if choice == 1:
            create_sample()
            print("Configure JSON and Run Version Updater")
        elif choice == 2:
            try:
                if bool(check_files()):
                    my_logger.logger.debug("**************** STARTS HERE **********************")
                    go = GitOperation('git_config.json')
                    go.git_clone()

                    local_rep_path = go.get_file_path()
                    cv = ChangeVersion.ChangeVersion('file_config.json', local_rep_path)
                    cv.replace_version()

                    f_list = cv.get_files_to_commit()

                    go.git_push(f_list)
                    dpath = go.get_file_path()

                    del go
                    print('\n\n')
                    time.sleep(2)
            except:
                my_logger.logger.error("Exception Occurred in Version Updater", exc_info=True)
                print("Exception Occurred in Version Updater!!")

        else:
            print("Not a valid choice")
    except:
        print('Not a Valid Choice !')
        my_logger.logger.error("Exception on Version Updater", exc_info=True)

    my_logger.logger.debug("**************** PROGRAM ENDED **********************")
    my_logger.logger.info("****************************************************")

    if dpath:
        print("Delete path:" + dpath)
        del_dir = input("Do you want to delete the created directory ? PRESS 'Y' or 'N' : ")

        if del_dir == 'Y' or del_dir == 'y':
            del_directory(dpath)

    close = input("Press Enter to Close !!")
    exit()
