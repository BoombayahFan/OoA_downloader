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

def on_start_process_downloaded_orders():
    directory_list = os.listdir(config["download_path"])
    for directory in directory_list:
        print("Processing {}".format(directory))
        hotfolder.create_json(directory)
    print("Processed all present directories")
        

if __name__ == '__main__':
    print("OoA Downloader {}".format(version))
    panel_api.authentication()
    on_start_process_downloaded_orders()
    hotfolder.observer.start()
    while True:
        time.sleep(1)



