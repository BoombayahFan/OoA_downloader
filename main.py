import time
import panel_api
import os
import hotfolder
from configuration import config

version = "1.0.0"


def get_number_of_folders(path):
    return len(os.listdir(path))


def get_oldest_folder(path):
    oldest = min(os.listdir(path), key=os.path.getctime)
    return oldest


if __name__ == '__main__':
    print("OoA Downloader {}".format(version))

    panel_api.authentication()

    os.chdir(config["download_path"])
    download_path = config["download_path"]

    while True:
        number_of_folders = get_number_of_folders(download_path)
        if number_of_folders == 0:
            pass
        else:
            folder_name = get_oldest_folder(download_path)
            if number_of_folders == 1:
                hotfolder.wait_for_full_download(folder_name)
                hotfolder.process_folder(folder_name)
            if number_of_folders > 1:
                hotfolder.process_folder(folder_name)

        time.sleep(0.5)
