from configuration import config
import os
import time
import panel_parse
import mrk_parser
import panel_api
import shutil
import random
import string
from datetime import datetime

QSS_PATH = config["destination_path"]

def wait_for_full_download(folder_name):
    time.sleep(1)
    try:
        images_path = os.path.join(config['download_path'], folder_name, "IMAGES")
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


def process_folder(folder_name):

    def generate_new_name(old_folder_name):
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
        new_folder_name = old_folder_name.replace("o", "t") + '_' + str(random_string)
        return new_folder_name

    def move_folder_to_qss_folder_using_new_name(old_folder_name, new_folder_name):
        src_path = os.path.join(os.getcwd(), old_folder_name)
        dst_path = os.path.join(QSS_PATH, new_folder_name)
        try:
            shutil.move(src_path, dst_path, copy_function=shutil.copy)
        except Exception as e:
            print(e)
        else:
            print('Moved directory {} to {}'.format(new_folder_name, QSS_PATH))

    def remove_details_file_from_folder(folder_name):
        delete_path = os.path.join(QSS_PATH, folder_name, "details.txt")
        try:
            os.remove(delete_path)
        except Exception as e:
            print(e)
            print("Failed to remove details.txt at {}".format(delete_path))

    def parse_data_from_folder(folder_name, new_folder_name):
        mrk_data = mrk_parser.parse(folder_name)
        order_data = {"deleted": False,
                      "archived": False,
                      "folder_name": new_folder_name}
        # Second append to order data - MRK data
        order_data.update(mrk_data)
        # Obsolete check - remains for compatibility
        order_data.update({"file_count_ok": True})

        order_data.update({"file_size_ok": True})
        # Fourth append to order data - data from panel
        sessions_id = panel_parse.download_sessions_id(mrk_data["panel_order_id"])
        suborder_id = sessions_id.get(mrk_data["session_count"])
        order_data.update({"panel_suborder_id": suborder_id})
        fast_package_value = panel_api.check_fast_package(order_data["panel_order_id"])
        order_data.update({"fast_package": fast_package_value})

        if suborder_id is None:
            order_data.update({"panel_suborder_id": "0"})

        if panel_api.send_new_suborder_to_ooa_web(order_data):
            print("Successfully processed order {} in folder {}".format(mrk_data["panel_order_id"], folder_name))
            return True
        else:
            for _ in range(10):
                if panel_api.send_new_suborder_to_ooa_web(order_data):
                    return True
            else:
                print("Failed to send order {}".format(folder_name))
                return False

    new_folder_name = generate_new_name(folder_name)
    if parse_data_from_folder(folder_name, new_folder_name):
        move_folder_to_qss_folder_using_new_name(folder_name, new_folder_name)
        time.sleep(0.5)
        remove_details_file_from_folder(new_folder_name)
    else:
        print("{} Folder {} was not accepted by OoA - restraining from moving folder".format(
            datetime.now().strftime("[%H:%M:%S]"), folder_name))


