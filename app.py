import os
import sys
import shutil
import requests
from zipfile import ZipFile

def exit_app():
    """ Exit program """
    input("Press Enter to exit")
    exit()

def check_version():
    """ Check latest release and update if any """
    response = requests.get('https://api.github.com/repos/SonicZedt/VStudent/releases')
    latest = response.json()[0]

    with open('VERSION', 'rb') as v:
        current = v.read().decode('utf-8')

    if latest['tag_name'][1:] == current:
        return

    print("\n===================")
    print(f"Current version : v{current}")
    print(f"New version available: {latest['tag_name']} at [{latest['html_url']}]")
    print("===================\n")

    def ask_update(verison_crt:str, version_lst:str, version_idx:int=0, version_thd:int=1):
        """ Ask user if they want to update
        params:\n
        str, version_crt, current version\n
        str, version_lst, latest version\n
        int, version_idx, character index in version string\n
        int, version_thd, threshold for version comparison """
        
        # check version gap
        verison_crt = verison_crt.replace('.', '')
        version_lst = version_lst.replace('.', '')
        if int(version_lst[version_idx]) - int(verison_crt[version_idx]) > version_thd:
            return True

        size = latest['assets'][0]['size']
        for _ in range(2):
            size = size/1024

        while True:
            choice = input(f"Do you want to update? ({round(size, 2)} MB) [Y/n]: ").lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid choice")
                continue

    def update():
        # write update to file
        sys.stdout.write("Downloading ... ")
        sys.stdout.flush()
        response = requests.get(latest['assets'][0]['browser_download_url'])
        update_name = latest['assets'][0]['name']
        with open(update_name, 'wb') as f:
            f.write(response.content)
            sys.stdout.write(f"Done\n")

        # extract update
        sys.stdout.write("Extracting ... ")
        sys.stdout.flush()
        with ZipFile(update_name, 'r') as zip:
            for file in zip.namelist():
                filename = file.split('/', 1)[1]
                if not os.path.basename(file):
                    continue

                source = zip.open(file)
                target = open(os.path.join(os.getcwd(), filename), 'wb')
                with source, target:
                    shutil.copyfileobj(source, target)
        sys.stdout.write(f"Done\n")

        # clean up update file
        sys.stdout.write("Cleaning up ... ")
        sys.stdout.flush()
        os.remove(update_name)
        sys.stdout.write(f"Done\n")

        print("Update complete, please restart the program")
        exit_app()

    if ask_update(current, latest['tag_name'][1:], 0, 1):
        update()