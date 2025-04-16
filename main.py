import time
import json
import requests
from datetime import datetime, timezone

# === CONFIG ===
REPLY_MESSAGE = "@{username} Oii massage maat kar warga nobi aa jaega"
REPLY_DELAY = 3  # seconds
COOKIES_JSON = """<PUT_YOUR_JSON_COOKIE_HERE>"""
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 14; Infinix X6739) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "x-ig-app-id": "936619743392459",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://www.instagram.com/direct/inbox/"
}

# === SETUP COOKIES ===
cookie_dict = {}
cookie_list = json.loads(COOKIES_JSON)
for c in cookie_list:
    cookie_dict[c['name']] = c['value']

session = requests.Session()
session.cookies.update(cookie_dict)
session.headers.update(HEADERS)


def get_threads():
    try:
        url = "https://www.instagram.com/api/v1/direct_v2/inbox/"
        res = session.get(url)
        if res.status_code == 200:
            return res.json().get("inbox", {}).get("threads", [])
        else:
            print(f"[!] Inbox error: {res.status_code}")
    except Exception as e:
        print(f"[!] Inbox fetch failed: {e}")
    return []


def is_bot_participant(thread):
    for user in thread.get("users", []):
        if user.get("pk") == cookie_dict.get("ds_user_id"):
            return True
    return False


def send_reply(thread_id, message, reply_to_item_id):
    url = "https://www.instagram.com/api/v1/direct_v2/threads/{}/items/".format(thread_id)
    data = {
        "action": "send_item",
        "item_type": "text",
        "text": message,
        "reply_type": "quote",
        "client_context": str(int(time.time() * 1000)),
        "mutation_token": str(int(time.time() * 1000)),
        "_csrftoken": cookie_dict.get("csrftoken"),
        "_uid": cookie_dict.get("ds_user_id"),
        "_uuid": cookie_dict.get("ig_did"),
        "reply_to_item_id": reply_to_item_id,
    }
    res = session.post(url, data=data)
    print(f"[+] Replied to thread {thread_id}: {res.status_code}")


seen_ids = set()
while True:
    threads = get_threads()
    for thread in threads:
        if not is_bot_participant(thread):
            continue

        if not thread.get("items"):
            continue

        last_item = thread["items"][0]
        item_id = last_item["item_id"]
        user_id = last_item.get("user_id") or last_item.get("sender_id")
        username = last_item.get("user", {}).get("username", "user")

        if item_id in seen_ids:
            continue

        seen_ids.add(item_id)
        mention_msg = REPLY_MESSAGE.replace("{username}", username)
        send_reply(thread_id=thread["thread_id"], message=mention_msg, reply_to_item_id=item_id)
        time.sleep(REPLY_DELAY)

    time.sleep(5)
