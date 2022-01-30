from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from configuration import config
import os
import time
import panel_parse
import mrk_parser
import json
import panel_api


def create_json(directory):
    time.sleep(0.2)
    try:
        # Declaring paths
        folder_path = "{}{}".format(config["download_path"], directory)
        json_path = folder_path + '\\order_data.json'

        if not os.path.isfile(json_path):
            # First append to order data
            order_data = {"deleted": False,
                          "archived": False,
                          "folder_name": directory}

            # Second append to order data - MRK data
            mrk_data = mrk_parser.parse(directory)
            order_data.update(mrk_data)

            # Obsolete check - remains for compatibility
            order_data.update({"file_count_ok": True})

            # Third append to order data - checks prints size
            for image in os.listdir(folder_path + "\\IMAGES"):
                pass
                # implement l8er
            else:
                order_data.update({"file_size_ok": True})

            # Fourth append to order data - data from panel
            sessions_id = panel_parse.download_sessions_id(mrk_data["order_id"])
            suborder_id = sessions_id.get(mrk_data["session_count"]) # wróciłem do tego po miesiącu i musiałem się 10 minut zastanawiać o chuj chodzi
            order_data.update({"suborder_id": suborder_id})

        # Dobra, najpierw musi wysłać do OoA_web, dostać 200 i dopiero wtedy może to zapisać - do dodanani

            # Save order data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, ensure_ascii=False, indent=4)

            print("Successfully processed {}".format(directory))
            return order_data
    except Exception as e:
        print("Failed to process {}\nError - {}".format(directory, e))


def on_created(event):
    path = os.path.split(event.src_path)
    filename = path[1]
    if filename == "AUTPRINT.MRK":
        parent_folder = os.path.split(path[0])[0]
        parent_folder = os.path.split(parent_folder)[1]
        print("AUTPRINT.MRK appears in folder {}".format(parent_folder))
        time.sleep(2)
        order_data = create_json(parent_folder)
        panel_api.send_new_suborder_to_OoA_web(order_data)


observer = Observer()
event_handler = FileSystemEventHandler()

event_handler.on_created = on_created
observer.schedule(event_handler, config["download_path"], recursive=True)

