import requests
import json
import time
from datetime import datetime, timezone

# Load cookies from session.json
with open("session.json", "r") as f:
    cookies = json.load(f)

# Create session and headers
session = requests.Session()
session.cookies.update(cookies)
user_id = cookies.get("ds_user_id")

headers = {
    "User-Agent": "Instagram 272.0.0.18.84 Android",
    "X-CSRFToken": cookies.get("csrftoken"),
}

BASE_URL = "https://i.instagram.com/api/v1"
REPLY_MESSAGE = "@{sender} Oii massage maat kar warga nobi aa jaega"
REPLY_DELAY = 3  # seconds
SEEN_INTERVAL = 60  # only reply to messages from the last 60 seconds

# Track replied message IDs and spammy groups
replied_ids = set()
spammy_groups = {}
blacklist = set()

def get_threads():
    url = f"{BASE_URL}/direct_v2/inbox/"
    res = session.get(url, headers=headers)
    return res.json().get("inbox", {}).get("threads", [])

def send_reply(thread_id, item_id, user_name):
    text = REPLY_MESSAGE.format(sender=user_name)
    payload = {"action": "send_item", "text": text}
    url = f"{BASE_URL}/direct_v2/threads/{thread_id}/items/text/"
    res = session.post(url, data=payload, headers=headers)
    if res.status_code == 200:
        print(f"[+] Replied to {user_name} in thread {thread_id}")
    else:
        print(f"[!] Failed to reply: {res.text}")

def should_skip_thread(thread):
    if not thread.get("is_group", False):
        return True
    if thread.get("thread_id") in blacklist:
        return True
    if not any(x.get("user_id") == user_id for x in thread.get("users", [])):
        print(f"[!] Skipping - kicked from group {thread.get('thread_title')}")
        return True
    return False

def process_threads():
    threads = get_threads()
    for thread in threads:
        thread_id = thread.get("thread_id")

        if should_skip_thread(thread):
            continue

        last_msg = thread.get("items", [])[0] if thread.get("items") else None
        if not last_msg:
            continue

        item_id = last_msg.get("item_id")
        timestamp = int(last_msg.get("timestamp", 0)) / 1000000
        sender = last_msg.get("user_id")

        if item_id in replied_ids:
            continue

        # Time check (only respond to recent messages)
        now = datetime.now(timezone.utc).timestamp()
        if now - timestamp > SEEN_INTERVAL:
            continue

        # Skip group name change spam
        if last_msg.get("item_type") == "placeholder":
            print(f"[!] Group name change spam detected, blacklisting {thread_id}")
            blacklist.add(thread_id)
            continue

        # Get sender's username
        sender_name = "unknown"
        for u in thread.get("users", []):
            if u["pk"] == sender:
                sender_name = u["username"]

        try:
            send_reply(thread_id, item_id, sender_name)
            replied_ids.add(item_id)
            time.sleep(REPLY_DELAY)
        except Exception as e:
            print(f"[!] Error replying: {e}")
            continue

# Main loop
print("Instagram roast bot started...")
while True:
    try:
        process_threads()
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n[!] Exiting bot.")
        break
    except Exception as e:
        print(f"[!] Main loop error: {e}")
        time.sleep(5)
