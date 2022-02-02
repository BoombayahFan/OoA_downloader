import re
from bs4 import BeautifulSoup
import panel_api


def download_sessions_id(order_id):
    try:
        soup = BeautifulSoup(panel_api.get_order_html(order_id), features="html.parser")
        prints_content = soup.find_all(class_="table printOrder")
        sessions_id = dict()
    except:
        print("No page was returned")
        return {"": None}
    for photo_prints in prints_content:
        try:
            session_number = photo_prints.find_all("td", {"colspan": 2})[0].text
            mrk_number = (re.findall("\[.*]", session_number))[0]
            print_id = photo_prints.get("order_id")
            sessions_id[mrk_number] = print_id
        except Exception as e:
            print(e)
            print("Brak odbitek w zamówieniu?")
    return sessions_id
