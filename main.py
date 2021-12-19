import time
import panel_api
import os
import json
import mrk_parser
import panel_parse
from configuration import config

version = "prealpha"


def process_downloaded_orders():
    directory_list = os.listdir(config["download_path"])
    blacklist_index = directory_list.index(config["blacklisted"])
    for i in range(config["items_to_load"]):

        # Declaring paths
        folder_name = directory_list[i + blacklist_index]
        folder_path = "{}{}".format(config["download_path"], folder_name)
        json_path = folder_path + '\\order_data.json'

        if not os.path.isfile(json_path):
            # First append to order data
            order_data = {"deleted": False,
                          "archived": False,
                          "folder_name": folder_name}

            # Second append to order data - MRK data
            mrk_data = mrk_parser.parse(folder_name)
            order_data.update(mrk_data)

            # Third append to order data - checks amount of prints
            if len(os.listdir(folder_path + "\\IMAGES")) != int(mrk_data["prints_count"]):
                order_data.update({"file_count_ok": False})
            else:
                order_data.update({"file_count_ok": True})

            # Fourth append to order data - checks prints size
            for image in os.listdir(folder_path + "\\IMAGES"):
                pass
                # implement l8er
            else:
                order_data.update({"file_size_ok": True})

            # Fifth append to order data - data from panel
            sessions_id = panel_parse.download_sessions_id(mrk_data["order_id"])
            suborder_id = sessions_id.get(mrk_data["session_count"])
            order_data.update({"suborder_id": suborder_id})

            # Save order data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, ensure_ascii=False, indent=4)

        i += 1


if __name__ == '__main__':
    print("OoA Downloader {}".format(version))
    panel_api.authentication()
    process_downloaded_orders()
