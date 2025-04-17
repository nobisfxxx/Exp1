import os
import time
import json
from datetime import datetime, timedelta, timezone
from instagrapi import Client
from instagrapi.types import DirectMessage

# ENV variables
username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
reply_text = os.getenv("REPLY_TEXT", "You're built like a toaster, bro.")
interval = int(os.getenv("CHECK_INTERVAL", 5))

# Files
session_file = "session.json"
last_login_file = "last_login.txt"

cl = Client()

def has_logged_in_today():
    if os.path.exists(last_login_file):
        with open(last_login_file, "r") as f:
            try:
                last = datetime.fromisoformat(f.read().strip())
                return datetime.now() - last < timedelta(hours=24)
            except:
                return False
    return False

def update_login_time():
    with open(last_login_file, "w") as f:
        f.write(datetime.now().isoformat())

def login_safely():
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                settings = json.load(f)
            cl.set_settings(settings)
            cl.get_timeline_feed()
            print("[+] Logged in using session.")
            return
        except Exception as e:
            print("[!] Session invalid, removing it:", e)
            os.remove(session_file)

    if has_logged_in_today():
        print("[!] Already logged in once today. Skipping login to avoid being flagged.")
        exit(1)

    try:
        cl.login(username, password)
        with open(session_file, "w") as f:
            json.dump(cl.get_settings(), f)
        update_login_time()
        print("[+] Logged in with username/password.")
    except Exception as e:
        print("[X] Login failed:", e)
        exit(1)

def is_recent(msg: DirectMessage) -> bool:
    if not msg.timestamp:
        return False
    now = datetime.now(timezone.utc)
    msg_time = msg.timestamp
    if msg_time.tzinfo is None:
        msg_time = msg_time.replace(tzinfo=timezone.utc)
    return (now - msg_time) < timedelta(seconds=60)

def reply_to_latest_unseen():
    threads = cl.direct_threads()
    for thread in threads:
        if len(thread.users) < 2:
            continue
        messages = cl.direct_messages(thread.id, amount=1)
        if not messages:
            continue
        last_msg = messages[0]
        if last_msg.user_id == cl.user_id:
            continue
        if not is_recent(last_msg):
            continue
        if last_msg.item_type != "text":
            continue

        user = cl.user_info(last_msg.user_id)
        mention_text = f"@{user.username} {reply_text}"
        try:
            cl.direct_send(mention_text, thread_ids=[thread.id], reply_to_message_id=last_msg.id)
            print(f"[+] Replied to {user.username} in thread {thread.id}")
        except Exception as e:
            print(f"[!] Error replying in thread {thread.id}: {e}")

# Start
login_safely()

while True:
    reply_to_latest_unseen()
    time.sleep(interval)
