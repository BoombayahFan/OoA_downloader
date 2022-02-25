import requests
from bs4 import BeautifulSoup
import re
import json
from configuration import config

login = config["panel_login"]
password = config["panel_password"]
crystal_api = requests.Session()


def authentication():
    try:
        authentication_url = 'https://panel.crystal-albums.pl/user/login/type/laborders/redirect/%252Flaborders'
        authentication_response = crystal_api.post(authentication_url,
                                                   data=dict(login=login,
                                                             password=password))

    except Exception as e:
        print("authentication error exception!")
        print(e)


def get_order_html(order_id):
    url = "https://panel.crystal-albums.pl/laborders/orders/edit/order_id/{}".format(order_id)
    r = crystal_api.get(url)
    try:
        if not r:
            print("Failed to download site!")
        else:
            return r.text
    except Exception as e:
        print(e)
        print("Critical error while requesting {}".format(url))


def change_session_status(order_id, session_id):
    url = "https://panel.crystal-albums.pl/laborders/status/changed/order_id/{}/id/{}?status_id=41&context=prints" \
        .format(order_id, session_id)
    r = crystal_api.post(url)


def delete_order_from_queue(order_id):
    url = "https://panel.crystal-albums.pl/laborders/machine/deteleprintsorder/from/detailedalbums/print_order_id/{}"\
        .format(order_id)
    r = crystal_api.get(url)

def send_new_suborder_to_OoA_web(some_json):
    ip = config["ip"]
    port = config["port"]
    url = "http://{}:{}/create_new_suborder".format(ip, port)
    r = requests.post(url, json=some_json)
    return r

