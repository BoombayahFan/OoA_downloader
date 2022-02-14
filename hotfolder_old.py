from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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

last_folder = ''
FOLDER_NAME_MAX_LENGHT = 7
WAIT_TIME = 3 # seconds


def get_mrk_information(directory):
    try:
        time.sleep(0.2)
        folder_path = "{}{}".format(config["orders_path"], directory)

        order_data = {"deleted": False,
                    "archived": False,
                    "folder_name": directory} #mam

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
        sessions_id = panel_parse.download_sessions_id(mrk_data["panel_order_id"])
        suborder_id = sessions_id.get(mrk_data["session_count"]) # wróciłem do tego po miesiącu i musiałem się 10 minut zastanawiać o chuj chodzi
        order_data.update({"panel_suborder_id": suborder_id})

        return order_data
    
    except Exception as e:
        print("Failed to process mrk {}\nError - {}".format(directory, e))


def change_name(json_data):
    folder_name = json_data['folder_name']

    if len(folder_name) < FOLDER_NAME_MAX_LENGHT:
        panel_order_id = json_data['panel_order_id']
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 15)) 

        new_folder_name = folder_name + '_' + str(panel_order_id) + '_' + str(random_string)
        folder_path = os.path.join(config['orders_path'], folder_name)
        new_file_path = os.path.join(config['orders_path'], new_folder_name)
        try:
            os.rename(folder_path, new_file_path)
            print('Sucessful rename {old} to {new}'.format(old=folder_name, new=new_folder_name))
        except Exception as e:
            print("Can't change folder name")
            print('Error - {}'.format(e))
    else:
        print("Folder name is to long, can't change name!")
        new_folder_name = folder_name

    return new_folder_name


def create_json(directory, order_data):
    try:
        # Declaring paths
        folder_path = "{}{}".format(config["orders_path"], directory)
        json_path = folder_path + '\\order_data.json'

        if not os.path.isfile(json_path):
            order_data.update({'folder_name' : directory})
            # Save order data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, ensure_ascii=False, indent=4)

            print("Successfully created json file to: {}".format(directory))
            return order_data

    except Exception as e:
        print("Failed to create json file {}\nError - {}".format(directory, e))


def send_to_web(order_data):
    if panel_api.send_new_suborder_to_OoA_web(order_data): # tutaj request
        print('Successful send to web') 
        pass
    else:
        print("OoA_downloader communication failed at {}".format('k'))


def process_order(directory):
    folder_path = "{}{}".format(config["orders_path"], directory)
    json_path = folder_path + '\\order_data.json'
    if len(directory) > FOLDER_NAME_MAX_LENGHT:
        return

    if not os.path.isfile(json_path):
        order_data = get_mrk_information(directory)             # pobranie danych z mrk i panelu
        new_directory = change_name(order_data)                 # zmiana nazwy folderu
        new_order_data = create_json(new_directory, order_data) # stworzenie json i zmiana folder_name w order_data
        send_to_web(new_order_data)                             # wysłanie order_data do web 
    
    else:
        order_data = dict
        with open(json_path, 'r', encoding="utf-8") as f:
            order_data = json.loads(f.read())

        send_to_web(order_data)


# function to move before the last one
def move_folder(directory):
    global last_folder
    if not directory == last_folder and not last_folder == '' and os.path.isdir(last_folder):
        file_path = os.path.join(config['download_path'], last_folder)
        size = -1
        print('size = {}'.format(size))

        while size != get_images_count(directory):
            size = get_images_count(directory)
            time.sleep(1)
            print(size)

        try:
            shutil.move(file_path, config["orders_path"], copy_function=shutil.copy)
            print('Moved directory: {}'.format(last_folder))

        except Exception as e:
            print(e)

    last_folder = directory
    folder_size = len(os.listdir(config['download_path']))
    if folder_size == 1:
        print('Processing last directory...')
        file_path = os.path.join(config['download_path'], directory)
        size = -1
        print('size = {}'.format(size))

        while size != get_images_count(directory):
            size = get_images_count(directory)
            time.sleep(1)

        time.sleep(WAIT_TIME)
        
        try:
            shutil.move(file_path, config["orders_path"], copy_function=shutil.copy)
            print('Moved directory: {}'.format(last_folder))

        except Exception as e:
            print(e)


def on_created_download(event):
    path = os.path.split(event.src_path)
    directory = path[0]
    file = path[1]
    global last_folder

    if not directory == last_folder and not last_folder == '':
        file_path = os.path.join(directory, last_folder)
        size = -1
        print('size = {}'.format(size))

        while size != get_images_count(last_folder):
            size = get_images_count(last_folder)
            time.sleep(1)
            print(size)

        try:
            shutil.move(file_path, config["orders_path"], copy_function=shutil.copy)
            print('Move directory: {}'.format(last_folder))

        except Exception as e:
            print(e)

    last_folder = file
    folder_size = len(os.listdir(config['download_path']))
    if folder_size == 1:
        print('Procesing last directory...')
        time.sleep(WAIT_TIME)
        file_path = os.path.join(directory, file)
        size = -1
        print('size = {}'.format(size))

        while size != get_images_count(file):
            size = get_images_count(file)
            time.sleep(1)
            print(size)

        try:
            shutil.move(file_path, config["orders_path"], copy_function=shutil.copy)    
            print('Move directory: {}'.format(last_folder))

        except Exception as e:
            print(e)

def on_created_order(event):
    path = os.path.split(event.src_path)
    filename = path[1]
    if filename == "AUTPRINT.MRK":
        parent_folder = os.path.split(path[0])[0]
        parent_folder = os.path.split(parent_folder)[1]
        print("AUTPRINT.MRK appears in folder {}".format(parent_folder))
        time.sleep(2)
        process_order(parent_folder)
