import time
import ChangeVersion
import GitOperation
import my_logger
import json
import shutil
import stat
import os
import threading
from colorama import init, Fore

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


def remove_access_denied(func, path, excinfo):
    os.chmod(path, stat.S_IWUSR)
    func(path)


def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def del_directory(d_path):
    shutil.rmtree(d_path, onerror=remove_access_denied, ignore_errors=True)
    shutil.rmtree(d_path, onerror=remove_readonly, ignore_errors=True)
    for root, dirs, files in os.walk(d_path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(d_path)
    my_logger.logger.info("Existing Directory Deleted successfully")


def main_thread():
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
                    go = GitOperation.GitOperation('git_config.json')
                    go.git_pull()

                    cv = ChangeVersion.ChangeVersion('file_config.json')
                    cv.replace_version()

                    go.git_push()

                    print('\n\n')
                    time.sleep(2)
                else:
                    print("File not found")

            except:
                my_logger.logger.error("Exception Occurred in Version Updater", exc_info=True)
                print("Exception Occurred in Version Updater!!")

        else:
            print("Not a valid choice")
    except:
        print('Not a Valid Choice')
        my_logger.logger.error("Exception on Version Updater", exc_info=True)

    my_logger.logger.debug("**************** PROGRAM ENDED **********************")
    my_logger.logger.info("****************************************************")


def delete_dir_thread(dpath):
    print("Dpath:"+dpath)
    del_dir = input("Do you want to delete the created directory ? PRESS 'Y' or 'N' : ")
    if del_dir == 'Y' or del_dir == 'y':
        del_directory(dpath)
        print("Directory deleted successfully")
        my_logger.logger.info("Directory deleted successfully")


if __name__ == '__main__':
    try:
        m_thrd = threading.Thread(target=main_thread)

        m_thrd.start()
        m_thrd.join()

        dpath = GitOperation.file_path
        del_thrd = threading.Thread(target=delete_dir_thread, args=(dpath,))

        del_thrd.start()
        del_thrd.join()
        close = input("Press Enter to close")
        exit()
    except:
        pass
