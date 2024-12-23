import json
import re
import sqlite3
import time
import requests
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
DATABASE_NAME = "my_database.db"
TELEGRAM_TOKEN = "1054213404:AAE9HZylcRi0cmJFToG-pvothnaJmltCb94"
TELEGRAM_CHAT_IDS = [572922903, 928826776]
DIVAR_API_URL = "https://api.divar.ir/v8/map-discovery/bbox/posts"
DIVAR_POST_URL_TEMPLATE = "https://divar.ir/v/{token}"
DATA_FETCH_INTERVAL = 380  # Seconds
LONG_WAIT_INTERVAL = 600  # Seconds
MAX_IMAGE_RETRY = 5
cookies = {
    'did': '8176a080-6bf4-4645-af19-0c2049aca52d',
    'multi-city': 'tehran%7C',
    'city': 'tehran',
    'LANGUAGE': 'fa',
    'cdid': '66466d3f-c77f-499a-9a88-d2f0ec8c4cd8',
    'theme': 'dark',
    '_gcl_au': '1.1.1238437121.1731494044',
    'ff': '%7B%22f%22%3A%7B%22custom_404_experiment%22%3Atrue%2C%22enable_new_post_card_web%22%3Atrue%2C%22chat_translate_enabled%22%3Atrue%2C%22post-card-title-top%22%3Atrue%2C%22new_post_card_is_small%22%3Atrue%2C%22new_post_card_left_img%22%3Atrue%7D%2C%22e%22%3A1732040105231%7D',
    '_gid': 'GA1.2.1295539138.1732036506',
    '_ga': 'GA1.1.1771160261.1703497474',
    'rwv_init_params': '',
    'csid': '',
    '_ga_SXEW31VJGJ': 'GS1.1.1732036506.4.1.1732036512.54.0.0',
    '_ga_WC29FSMWTF': 'GS1.1.1732036521.2.1.1732036750.36.0.0',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
    'cache-control': 'no-cache',
    # 'cookie': 'did=8176a080-6bf4-4645-af19-0c2049aca52d; multi-city=tehran%7C; city=tehran; LANGUAGE=fa; cdid=66466d3f-c77f-499a-9a88-d2f0ec8c4cd8; theme=dark; _gcl_au=1.1.1238437121.1731494044; ff=%7B%22f%22%3A%7B%22custom_404_experiment%22%3Atrue%2C%22enable_new_post_card_web%22%3Atrue%2C%22chat_translate_enabled%22%3Atrue%2C%22post-card-title-top%22%3Atrue%2C%22new_post_card_is_small%22%3Atrue%2C%22new_post_card_left_img%22%3Atrue%7D%2C%22e%22%3A1732040105231%7D; _gid=GA1.2.1295539138.1732036506; _ga=GA1.1.1771160261.1703497474; rwv_init_params=; csid=; _ga_SXEW31VJGJ=GS1.1.1732036506.4.1.1732036512.54.0.0; _ga_WC29FSMWTF=GS1.1.1732036521.2.1.1732036750.36.0.0',
    'origin': 'https://divar.ir',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://divar.ir/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-internal-device-id': '8176a080-6bf4-4645-af19-0c2049aca52d',
}


# Database initialization
def initialize_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS my_table (
                vadie TEXT,
                ejare TEXT,
                location TEXT,
                link TEXT UNIQUE,
                title TEXT,
                city TEXT

            )
        '''
        cursor.execute(create_table_query)
        conn.commit()
        logging.info("Database initialized.")


# Database operations
def check_and_insert(data: dict) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM my_table WHERE link=?", (data["link"],))
        if cursor.fetchone():
            logging.info(f"Record already exists for link: {data['link']}")
            return False
        cursor.execute(
            "INSERT INTO my_table (vadie, ejare, location, link, title,city) VALUES (?, ?, ?, ?, ?, ?)",
            (data["vadie"], data["ejare"], data["location"], data["link"], data["title"], data["city"]),
        )
        conn.commit()
        logging.info(f"New record inserted for link: {data['link']}")
        return True


# Telegram messaging
def build_images_data(images: List[str], caption: str) -> str:
    image_data = [{"type": "photo", "media": image} for image in images]
    image_data[0]["caption"] = caption
    return json.dumps(image_data)


def send_message(data: dict, images: List[str] = None):
    message = (
        f"➿➿➿➿➿{data['city']}➿➿➿➿➿\n"
        f"💢 {data['title']} 💢\n"
        f"💲 {data['ejare']}\n"
        f"💰 {data['vadie']}\n"
        f"🚩 {data['location']}\n"
        f"🔗 {data['link']}\n"
        "〰〰〰〰〰〰〰〰〰〰〰"
    )
    method = "sendMessage"
    payload_key = "text"
    payload = {"chat_id": TELEGRAM_CHAT_IDS[0], payload_key: message}

    if images:
        method = "sendMediaGroup"
        payload_key = "media"
        payload = {"chat_id": TELEGRAM_CHAT_IDS[0], payload_key: build_images_data(images, message)}

    for chat_id in TELEGRAM_CHAT_IDS:
        payload["chat_id"] = chat_id
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}", data=payload
        )
        if response.status_code == 200:
            logging.info(f"Message sent successfully to chat ID: {chat_id}")
        else:
            logging.error(f"Failed to send message to chat ID: {chat_id}: {response.text}")


# Data fetching
def fetch_divar_posts(url):
    try:
        response = requests.get(url,
                                cookies=cookies,
                                headers=headers,
                                )
        response.raise_for_status()
        return response.json().get("posts", [])
    except requests.RequestException as e:
        logging.error(f"Failed to fetch posts: {e}")
        return []


def fetch_post_images(post_token: str) -> List[str]:
    for attempt in range(MAX_IMAGE_RETRY):
        try:
            response = requests.get(DIVAR_POST_URL_TEMPLATE.format(token=post_token), cookies=cookies, headers=headers)
            if response.status_code == 200:
                images = re.findall(r"https?://[^\s\"]+/post/[^\s\"]+\.jpg", response.text)
                if not images:
                    time.sleep(3)
                    continue
                else:
                    return images
            time.sleep(5)
        except requests.RequestException:
            logging.warning(f"Retrying image fetch for token: {post_token} (attempt {attempt + 1})")
    logging.error(f"Failed to fetch images for token: {post_token} after {MAX_IMAGE_RETRY} attempts.")
    return []


def process_posts(posts, city):
    for post in posts:
        try:
            title = post["title"]
            if any(keyword in post["title"] for keyword in
                   ["همخونه", "هم خونه", "هم خانه", "همخانه", "فاز۱۱", "فاز۹", "فاز۵", "فاز11", "فاز9", "فاز۸",
                    "فاز8", "فاز5"
                       , "فاز ۱۱", "فاز ۹", "فاز ۵", "فاز 11", "فاز 9", "فاز ۸",
                    "فاز 8", "فاز 5"

                    ]):
                continue
            data = {
                "title": post["title"],
                "city": city,
                "link": DIVAR_POST_URL_TEMPLATE.format(token=post["token"]),
                "vadie": post["subtitle1"],
                "ejare": post["subtitle2"],
                "location": post["subtitle3"],
            }
            if check_and_insert(data):
                time.sleep(10)
                images = fetch_post_images(post["token"])

                send_message(data, images)

        except KeyError:
            logging.warning("Malformed post data skipped.")


# Main loop
def main():
    initialize_database()
    while True:
        posts_pardis = fetch_divar_posts(
            "https://api.divar.ir/v8/map-discovery/bbox/posts?lon1=51.789898817396534&lat1=35.7081983481158&lon2=51.81747464959125&lat2=35.76816566191087&nextPageId=0&filters=category=residential-rent&filters=credit=50000000-200000000&filters=geo_polygon_encoded=w%7BdyEwgb%7BHyMP%7DIiCyMsO%7BIyQcH_%5CcEm%5B%7DBs%5D%5Bu%5E%60IkmAxM_c%40vQsVfNuItQ%7DDfU%3FxMfBzIxCtN%7CLfNxQ~EzRZ%7Cp%40eKxdAcEbHkMvBuDfCwCbs%40qE%60VcHfQqE%60GgNvIeKvB&filters=rent=2000000-10000000&filters=rooms=%D8%AF%D9%88")
        posts_tehran = fetch_divar_posts(
            'https://api.divar.ir/v8/map-discovery/bbox/posts?lon1=51.315885048326635&lat1=35.64137054628955&lon2=51.38507385697949&lat2=35.79187146855938&nextPageId=0&filters=category=residential-rent&filters=credit=100000000-200000000&filters=geo_polygon_encoded=m~gyE%7DyzwHweA%60Vyl%40rj%40mImrB%7DWu%7CB%3F%7DbSmIem%40fEonAvQwxAld%40%7BfAzgA%7Bt%40hy%40wxAd%5Ey%5DtcA%7DP%60Z%60VtO%3F%60Zm%60BxS_QvQ%3FpM~Pth%40fI%60s%40h%7BAh%60%40piCfEniC%7CUfvAdgBvo%40h%60%40le%40f%5EhmBaAtnCqMb_Aky%40vxAy~AzfAikBlw%40cs%40pj%40qf%40zKc%5CrXiGp%7C%40ykDpiC&filters=rent=3000000-10000000&filters=rooms=%D8%AF%D9%88',
        )
        process_posts(posts_pardis, "Pardis")
        time.sleep(5)
        process_posts(posts_tehran, "Tehran")
        logging.info("Waiting for the next fetch cycle...")
        time.sleep(DATA_FETCH_INTERVAL)


if __name__ == "__main__":
    main()
