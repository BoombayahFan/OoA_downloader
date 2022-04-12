import configparser
import re
import os
from configuration import config


def parse(folder_name):

    def convert_channel_to_roll(channel_str):
        try:
            channel = int(channel_str)
            roll_15_channels = config["roll_15_channels"]
            roll_13_channels = config["roll_13_channels"]
            roll_30_channels = config["roll_30_channels"]
            if channel in roll_15_channels:
                return 15
            if channel in roll_13_channels:
                return 13
            if channel in roll_30_channels:
                return 30
        except:
            return 0

    def read_channel():
        try:
            channel = mrk_parser["HDR"]["PRT PCH"]
            return channel
        except:
            print("Failed to read MRK channel at {}".format(path))
            return 0

    def read_order_id():
        try:
            order_id = mrk_parser["JOB"]["PRT CVP1"]
            order_id = re.findall('".*\[', order_id)
            order_id = order_id[0][1:-2]
            return order_id
        except:
            print("Failed to read MRK order_id at {}".format(path))
            return "0"

    def read_session_count():
        try:
            session_count = mrk_parser["JOB"]["PRT CVP1"]
            session_count = re.findall('\[.*]', session_count)
            return session_count[0]
        except:
            print("Failed to read MRK session_count at {}".format(path))
            return "0"

    def read_prints_count():
        try:
            prints_count = mrk_parser["JOB"]["PRT CVP2"]
            prints_count = re.findall('\/.*\]', prints_count)
            prints_count = prints_count[0][1:-1]
            return prints_count
        except:
            print("Failed to read MRK prints_count at {}".format(path))
            return 0

    def read_prints_format():
        try:
            print_format = mrk_parser["JOB"]["PRT CVP2"]
            print_format = re.findall('szt. .....', print_format)
            print_format = print_format[0][5:]
            return print_format
        except:
            print("Failed to read MRK prints_format at {}".format(path))
            return "0"

    def read_suborder_name():
        try:
            suborder_name = mrk_parser["JOB"]["PRT CVP1"]
            suborder_name = re.findall('\]\/.*', suborder_name)
            suborder_name = suborder_name[0][2:-1]
            return suborder_name
        except:
            print("Failed to read MRK suborder_name at {}".format(path))
            return "???"

    path = os.path.join(config["destination_path"], folder_name, "MISC", "AUTPRINT.MRK")

    mrk_parser = configparser.ConfigParser(strict=False)

    try:
        if os.path.isfile(path):
            mrk_parser.read(path, encoding="utf-8")
            mrk_present = True
        else:
            print("File at {} does not exist".format(path))
            raise Exception
    except Exception as e:
        mrk_present = False
        print(e)
        print("Failed to read MRK file at {}".format(path))

    return {"mrk_exists": mrk_present,
            "channel": read_channel(),
            "panel_order_id": read_order_id(),
            "prints_count": read_prints_count(),
            "prints_format": read_prints_format(),
            "roll": convert_channel_to_roll(read_channel()),
            "session_count": read_session_count(),
            "suborder_name": read_suborder_name(),
            "is_archived": False}
