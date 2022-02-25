from configuration import config
import os
import time
import panel_parse
import mrk_parser
import json
import panel_api
import shutil
import random
import string


def move_folder(folder_name):
    source_path = os.path.join(config['download_path'], folder_name)
    new_folder_name = folder_name.replace("o", "t")
    try:
        shutil.move(source_path, "{}{}".format(config["destination_path"], new_folder_name), copy_function=shutil.copy)
        print('Moved directory: {}'.format(folder_name))
        return new_folder_name

    except Exception as e:
        print(e)


def wait_for_full_download(folder_name):
    time.sleep(1)
    try:
        images_path = "{}{}\\{}\\".format(config['download_path'], folder_name, "IMAGES")
        current_images_count = len(os.listdir(images_path))
        i = 0
        TIMEOUT = config['timeout']*10
        while True:
            previous_images_count = current_images_count
            current_images_count = len(os.listdir(images_path))
            if current_images_count == previous_images_count:
                i += 1
            else:
                i = 0
            time.sleep(0.1)
            # Pretty output
            print("\rWaiting for {} to complete download {}".format(folder_name, TIMEOUT - i), end="")
            if i >= TIMEOUT:
                print("\rFolder {} downloaded".format(folder_name))
                break
    except Exception as e:
        print(e)
        print("An error occurred while waiting for full download - it seems there are no images in {}".format(folder_name))


def process_suborder_folder(folder_name):
    def generate_new_folder_name():
        panel_order_id = mrk_data['panel_order_id']
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        new_folder_name = folder_name.replace("o", "t") + '_' + str(panel_order_id) + '_' + str(random_string)

        return new_folder_name
    time.sleep(0.5)
    mrk_data = mrk_parser.parse(folder_name)
    src = "{}{}".format(config["destination_path"], folder_name)

    new_folder_name = generate_new_folder_name()
    dst = "{}{}".format(config["destination_path"], new_folder_name)

    shutil.move(src, dst)

    order_data = {"deleted": False,
                  "archived": False,
                  "folder_name": new_folder_name}
    # Second append to order data - MRK data
    order_data.update(mrk_data)
    # Obsolete check - remains for compatibility
    order_data.update({"file_count_ok": True})
    # Third append to order data - checks prints size
    """for image in os.listdir(folder_name + "\\IMAGES"):
        pass
        # implement l8er
    else:"""
    order_data.update({"file_size_ok": True})
    # Fourth append to order data - data from panel
    sessions_id = panel_parse.download_sessions_id(mrk_data["panel_order_id"])
    suborder_id = sessions_id.get(mrk_data["session_count"])
    order_data.update({"panel_suborder_id": suborder_id})
    if suborder_id is None:
        order_data.update({"panel_suborder_id": "0"})

    if panel_api.send_new_suborder_to_OoA_web(order_data):
        print("Successfully processed order {} in folder {}".format(mrk_data["panel_order_id"], new_folder_name))
    else:
        for _ in range(10):
            if panel_api.send_new_suborder_to_OoA_web(order_data):
                break
        else:
            print("Failed to send order {}".format(new_folder_name))
