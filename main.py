import os
import time
from datetime import datetime, timedelta, timezone
from instagrapi import Client
from instagrapi.types import DirectMessage

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
reply_text = os.getenv("REPLY_TEXT", "You're built like a toaster, bro.")
interval = int(os.getenv("CHECK_INTERVAL", 5))

cl = Client()
cl.login(username, password)
print("[+] Logged in.")

def is_recent(msg: DirectMessage) -> bool:
    if not msg.timestamp:
        return False
    now = datetime.now(timezone.utc)
    return (now - msg.timestamp) < timedelta(seconds=60)

def reply_to_latest_unseen():
    threads = cl.direct_threads()
    for thread in threads:
        if len(thread.users) < 2:
            continue
        if not thread.items:
            continue
        last_msg = thread.items[0]
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

while True:
    reply_to_latest_unseen()
    time.sleep(interval)
