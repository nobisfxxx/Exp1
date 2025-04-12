from instagrapi import Client
import os
import time
import json
from datetime import datetime, timezone, timedelta

# --- CONFIG ---
USERNAME = "bot_hu_yaa"
PASSWORD = "nobihuyaar@11"
SESSION_FILE = "insta_session.json"
REPLY_MESSAGE = "oye @{}, tu toh itna boring hai ke mute karne ka mann kar raha hai"
DEVICE_SETTINGS = {
    "app_version": "272.0.0.18.84",
    "android_version": 34,
    "android_release": "14",
    "dpi": "480dpi",
    "resolution": "1080x2400",
    "manufacturer": "infinix",
    "device": "Infinix-X6739",
    "model": "Infinix X6739",
    "cpu": "mt6893"
}

cl = Client()
cl.set_device(DEVICE_SETTINGS)

def login():
    if os.path.exists(SESSION_FILE):
        print("Loading saved session...")
        cl.load_settings(SESSION_FILE)
        try:
            cl.get_timeline_feed()
            print("Session login successful.")
            return
        except Exception as e:
            print("Session expired or invalid, logging in fresh.")
    
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("Logged in and session saved.")

def is_recent(msg_time):
    now = datetime.now(timezone.utc)
    return (now - msg_time) <= timedelta(seconds=60)

last_reply_time = {}
group_blacklist = {}

def auto_reply_all_groups():
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if len(thread.users) <= 2:
                    continue
                if not thread.viewer.is_active:
                    print(f"[SKIPPED] Removed from group '{thread.thread_title}'")
                    continue

                thread_id = thread.id
                try:
                    thread_data = cl.direct_thread(thread_id)
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
                    continue

                if group_blacklist.get(thread_id, 0) > 10:
                    print(f"[SKIPPED] Spammy group '{thread.thread_title}' (blacklisted)")
                    continue

                if thread_data.messages:
                    last_msg = thread_data.messages[0]

                    # Skip name change/system events
                    if not hasattr(last_msg, "text") or last_msg.user_id == cl.user_id:
                        continue

                    if not is_recent(last_msg.timestamp):
                        continue

                    # Only reply every 3 seconds max per group
                    last = last_reply_time.get(thread_id, 0)
                    if time.time() - last < 3:
                        continue

                    try:
                        sender_username = cl.user_info(last_msg.user_id).username
                        roast = REPLY_MESSAGE.format(sender_username)
                        cl.direct_send(roast, thread_ids=[thread_id])
                        print(f"[REPLIED] @{sender_username} in '{thread.thread_title}'")
                        last_reply_time[thread_id] = time.time()
                    except Exception as e:
                        print(f"Error replying in {thread_id}: {e}")
        except Exception as e:
            print(f"Main loop error: {e}")

        time.sleep(5)

# Start
login()
auto_reply_all_groups()
