import json
import requests
import time
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


def get_products_id_list(order_id):  # order_id to numer zlecenia w panelu
    try:
        target_url = 'https://panel.crystal-albums.pl/laborders/api/orderalbums/order_id/'
        return crystal_api.get(target_url+str(order_id)).text
    except Exception as e:
        print("get_products_id_list method error!")
        print(e)


def get_product_details(product_id):
    try:
        target_url = 'https://panel.crystal-albums.pl/laborders/api/album/album_order_config_id/{}'.format(product_id)
        return crystal_api.get(target_url).text
    except Exception as e:
        print("get_product_details method error!")
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


def send_new_suborder_to_ooa_web(some_json):
    ip = config["ip"]
    port = config["port"]
    url = "http://{}:{}/create_new_suborder".format(ip, port)
    r = requests.post(url, json=some_json)
    return r


def check_fast_package(order_id):

    fast_package_products = config["fast_package_products"]

    try:
        orders_ids = json.loads(get_products_id_list(order_id))
        if len(orders_ids) == 0:
            return 3  # 'odbitki'
        else:
            for order_id in orders_ids:
                product_data = json.loads(get_product_details(order_id))

                if product_data['Linia'] in fast_package_products:
                    pass
                else:
                    return 1  # 'album'
            else:
                return 2  # szybka paczka

    except:
        print('album except')
        return 3


