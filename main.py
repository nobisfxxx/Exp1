import os
import time
from datetime import datetime, timedelta, timezone
from instagrapi import Client
from instagrapi.types import DirectMessage
import json

# Environment variables
username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")
reply_text = os.getenv("REPLY_TEXT", "You're built like a toaster, bro.")
interval = int(os.getenv("CHECK_INTERVAL", 5))
session_file = "session.json"  # Path to store the session data

# Initialize the Instagram client
cl = Client()

# Function to login once a day using session
def login_once_a_day():
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            if cl.is_logged_in:
                print("[+] Logged in using session.")
                return
        except json.JSONDecodeError:
            print("[!] Session file is empty or corrupted. Logging in again and creating a new session.")
            os.remove(session_file)  # Remove corrupted session file

    # Login if session is not available or expired
    cl.login(username, password)
    print("[+] Logged in.")

    # Save session to the session file for future use
    cl.save_settings(session_file)

# Ensure we login once and load the session
login_once_a_day()

def is_recent(msg: DirectMessage) -> bool:
    if not msg.timestamp:
        return False
    
    # Ensure the timestamp is timezone-aware
    if msg.timestamp.tzinfo is None:
        msg.timestamp = msg.timestamp.replace(tzinfo=timezone.utc)

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

# Run the bot
while True:
    reply_to_latest_unseen()
    time.sleep(interval)
