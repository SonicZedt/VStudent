import os
import sys
import requests
import shutil
import argparse
from zipfile import ZipFile

class App:
    def __init__(self, version_crt):
        self.version_crt = version_crt
        self.version_lts = None
        self.name = ''
        self.updated = False

    @property
    def tag(self) -> str:
        """ Latest release tag name """
        return self.version_lts['tag_name']

    @property
    def url(self) -> str:
        """ Latest release url """
        return self.version_lts['html_url']

    @property
    def version_gap(self) -> int:
        """ Version gap between current and latest release """
        current = int(self.version_crt.replace('.', ''))
        latest = int(self.version_lts['tag_name'][1:].replace('.', ''))

        return latest - current

    @property
    def size_byte(self):
        """ Size of latest release """
        return self.version_lts['assets'][0]['size']

    def get_size(self, volume:str='MB') -> str:
        """ Convert size in byte to another volume
        params: str, volume, volume to convert to """

        volume_dict = {
            'KB' : 1,
            'MB' : 2,
            'GB' : 3,
        }
        if volume.upper() not in volume_dict.keys():
            volume = 'KB'

        size = self.size_byte
        for _ in range(volume_dict[volume]):
            size = size/1024
        return f"{round(size, 2)} {volume.upper()}"

    def check(self) -> dict:
        """ Check if newer version/release is available
        returns: dict, latest release info if available """
        response = requests.get('https://api.github.com/repos/SonicZedt/VStudent/releases')
        latest = response.json()[0]

        if latest['tag_name'][1:] == self.version_crt:
            return None
        
        self.version_lts = latest
        return latest

    def download(self) -> str:
        """ Download and write latest release into file
        return: str, latest release name """
        if self.version_lts is None:
            self.check()

        # download latest release
        sys.stdout.write("Downloading ... ")
        sys.stdout.flush()
        response = requests.get(self.version_lts['assets'][0]['browser_download_url'])
        
        # write latest release into zip file
        release_name = self.version_lts['assets'][0]['name']
        with open(release_name, 'wb') as f:
            f.write(response.content)
            sys.stdout.write(f"Done\n")

        self.name = release_name
        return release_name

    def install(self):
        """ Install latest release by calling extract and clean up """
        if self.version_lts is None:
            return

        # install latest release
        self.extract()
        self.clean_up()
        self.confirm()

    def extract(self):
        """ Extract latest release into folder """
        if self.version_lts is None:
            return

        # extract latest release
        sys.stdout.write("Extracting ... ")
        sys.stdout.flush()
        with ZipFile(self.name, 'r') as zip:
            for file in zip.namelist():
                filename = file.split('/', 1)[1]

                # skip extract folder
                if not os.path.basename(file):
                    continue

                source = zip.open(file)
                target = open(os.path.join(os.getcwd(), filename), 'wb')
                with source, target:
                    shutil.copyfileobj(source, target)
        sys.stdout.write(f"Done\n")
        self.updated = True

    def clean_up(self):
        """ Clean up update files """
        if self.version_lts is None:
            return

        # clean up update files
        sys.stdout.write("Cleaning up ... ")
        sys.stdout.flush()
        os.remove(self.name)
        sys.stdout.write(f"Done\n")

    def confirm(self):
        if self.updated:
            print("\nUpdate complete, please launch vsg.exe again")
            confirm_exit()
        else:
            print("\nFailed to update")
            confirm_exit()

def confirm_exit():
    input("Press Enter to exit")
    exit()

def update_app(update:App):
    """ Begin app update progress """
    print(f"Starting update {update.tag} sequence ...")
    update.download()
    update.install()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update_app', default=False, action='store_true', help="update app")
    parser.add_argument('--version_crt', default='0.0.0', type=str, help="current version")
    args = parser.parse_args()

    if not args.update_app:
        return

    update = App(args.version_crt)
    update.check()
    update_app(update)

if __name__ == '__main__':
    main()