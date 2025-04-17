import os
import time
import json
from datetime import datetime, timedelta, timezone
from instagrapi import Client
from instagrapi.types import DirectMessage

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
reply_text = os.getenv("REPLY_TEXT", "You're built like a toaster, bro.")
interval = int(os.getenv("CHECK_INTERVAL", 5))
session_file = "session.json"

cl = Client()
last_keep_alive = time.time()

def login_once_a_day():
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                cl.load_settings(json.load(f))
            cl.login(username, password)
            print("[+] Logged in using session.")
            return
        except Exception as e:
            print(f"[!] Failed to load session: {e}")

    cl.login(username, password)
    with open(session_file, "w") as f:
        json.dump(cl.get_settings(), f)
    print("[+] Logged in with username/password.")

def is_recent(msg: DirectMessage) -> bool:
    if not msg.timestamp:
        return False
    now = datetime.now(timezone.utc)
    msg_time = msg.timestamp.replace(tzinfo=timezone.utc) if msg.timestamp.tzinfo is None else msg.timestamp
    return (now - msg_time) < timedelta(seconds=60)

def reply_to_latest_unseen():
    threads = cl.direct_threads()
    for thread in threads:
        if len(thread.users) < 2 or not thread.items:
            continue
        last_msg = thread.items[0]
        if last_msg.user_id == cl.user_id:
            continue
        if not is_recent(last_msg):
            continue
        if last_msg.item_type != "text":
            continue
        try:
            user = cl.user_info(last_msg.user_id)
            mention_text = f"@{user.username} {reply_text}"
            cl.direct_send(mention_text, thread_ids=[thread.id])
            print(f"[+] Replied to {user.username} in thread {thread.id}")
        except Exception as e:
            print(f"[!] Error replying in thread {thread.id}: {e}")

def keep_alive_ping():
    global last_keep_alive
    if time.time() - last_keep_alive > 600:  # every 10 minutes
        try:
            cl.get_timeline_feed()  # simple keep-alive call
            last_keep_alive = time.time()
            print("[*] Keep-alive ping sent.")
        except Exception as e:
            print(f"[!] Keep-alive error: {e}")

login_once_a_day()

while True:
    reply_to_latest_unseen()
    keep_alive_ping()
    time.sleep(interval)
