import os
import updater

def exit_app():
    """ Exit program """
    input("Press Enter to exit")
    exit()

def check_version():
    """ Check latest release and update if any """
    with open('VERSION', 'rb') as v:
        current = v.read().decode('utf-8')
    
    update = updater.App(current)
    update_info = update.check()

    if update_info is None:
        return

    print("\n===================")
    print(f"Current version : v{current}")
    print(f"New version available: {update.tag} at [{update.url}]")
    print("===================\n")

    def ask_update(version_thd:int=10):
        """ Ask user if they want to update
        params: int, version_idx, character index in version string
        params: int, version_thd, threshold for version comparison """
        
        if update.version_gap > version_thd:
            return True

        while True:
            choice = input(f"Do you want to update? ({update.get_size()}) [Y/n]: ").lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid choice")
                continue

    if ask_update(10):
        # Launch updater.exe
        os.system('start updater.exe --update_app --version_crt ' + current)
        exit()