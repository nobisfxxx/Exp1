import os
import time
from datetime import datetime, timedelta, timezone
from instagrapi import Client
from instagrapi.types import DirectMessage

# Environment variables
username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
reply_text = os.getenv("REPLY_TEXT", "You're built like a toaster, bro.")
interval = int(os.getenv("CHECK_INTERVAL", 5))
session_file = "session.json"

# Initialize the client
cl = Client()

def login_once_a_day():
    """Logs in once a day and saves the session."""
    if os.path.exists(session_file):
        # Try loading session from file
        cl.load_settings(session_file)
        try:
            cl.login(username, password)
            print("[+] Logged in using session.")
            return
        except Exception as e:
            print("[!] Session expired or invalid, logging in again:", e)

    # Login using username and password if no valid session exists
    cl.login(username, password)
    cl.dump_settings(session_file)
    print("[+] Logged in and session saved.")

# Perform login once at the start
login_once_a_day()

def is_recent(msg: DirectMessage) -> bool:
    """Check if the message is recent (within the last 60 seconds)."""
    if not msg.timestamp:
        return False
    now = datetime.now(timezone.utc)
    return (now - msg.timestamp) < timedelta(seconds=60)

def reply_to_latest_unseen():
    """Replies to the latest unseen message."""
    threads = cl.direct_threads()
    for thread in threads:
        if len(thread.users) < 2:
            continue
        if not thread.messages:
            continue
        last_msg = thread.messages[0]
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

# Run the bot periodically
while True:
    reply_to_latest_unseen()
    time.sleep(interval)
