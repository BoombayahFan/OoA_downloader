import time
import panel_api
import os
import hotfolder
from configuration import config

version = "alpha"

# na wszelki jeśli znowu zapomnę skopiować pustych plików
"""directory_list = os.listdir(config["download_path"])
for directory in directory_list:
    folder_path = "{}{}{}".format(config["download_path"], directory,"\\order_data.json")
    os.remove(folder_path)
"""


if __name__ == '__main__':
    print("OoA Downloader {}".format(version))
    panel_api.authentication()

    while True:
        directory_list = os.listdir(config["download_path"])
        if len(directory_list) == 1:
            folder_name = directory_list[0]
            hotfolder.wait_for_full_download(folder_name)
            time.sleep(1)
            new_folder_name = hotfolder.move_folder(folder_name)
            hotfolder.process_suborder_folder(new_folder_name)
        elif len(directory_list) > 1:
            folder_name = directory_list[0]
            new_folder_name = hotfolder.move_folder(folder_name)
            hotfolder.process_suborder_folder(new_folder_name)
            time.sleep(1)

        else:
            pass
        time.sleep(0.5)
