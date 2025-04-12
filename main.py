from instagrapi import Client
from datetime import datetime, timedelta, timezone
import time
import json
import os

# --- CONFIG ---
USERNAME = "rdpofraaz"  # Your username
PASSWORD = "rudrakirdp"  # Your password
REPLY_MESSAGE = "oii massage maat kar warna paradox ki maa shod ke feekkk dunga"
SESSION_FILE = "session_cookies.json"  # Your session file
BLACKLIST_FILE = "blacklist.json"
REPLY_INTERVAL = 3  # seconds
# ----------------

device_settings = {
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
cl.set_device(device_settings)

# Load session
if os.path.exists(SESSION_FILE):
    try:
        cl.load_settings(SESSION_FILE)
        cl.get_timeline_feed()
        print("Logged in using saved session.")
    except Exception:
        print("Failed to load session: login_required")
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("Logged in using username/password and session saved.")
else:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("Logged in and session saved.")

# Load or initialize blacklist
if os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, 'r') as f:
        blacklisted_threads = set(json.load(f))
else:
    blacklisted_threads = set()

last_reply_time = time.time() - REPLY_INTERVAL
recent_name_changes = {}

def should_blacklist_group(thread):
    thread_id = thread.id
    name_changes = recent_name_changes.get(thread_id, [])
    # Clean up old name change records
    name_changes = [t for t in name_changes if time.time() - t < 10]
    if len(name_changes) >= 5:
        return True
    recent_name_changes[thread_id] = name_changes
    return False

def auto_reply_all_groups():
    global last_reply_time
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if thread.inviter is None or len(thread.users) <= 2:
                    continue

                thread_id = thread.id

                # Skip blacklisted threads
                if thread_id in blacklisted_threads:
                    continue

                # Fetch latest message
                try:
                    thread_data = cl.direct_thread(thread_id)
                    if thread_data is None:
                        continue
                    messages = thread_data.messages
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
                    continue

                for msg in reversed(messages):  # Check latest message only
                    if msg.user_id == cl.user_id:
                        break  # Don't reply to own message

                    if hasattr(msg, 'item_type') and msg.item_type == 'action_log':
                        # Group name change
                        recent_name_changes.setdefault(thread_id, []).append(time.time())
                        if should_blacklist_group(thread):
                            print(f"Blacklisting spammy group: {thread_id}")
                            blacklisted_threads.add(thread_id)
                            with open(BLACKLIST_FILE, 'w') as f:
                                json.dump(list(blacklisted_threads), f)
                        break

                    # Only reply if 3s passed
                    if time.time() - last_reply_time >= REPLY_INTERVAL:
                        try:
                            username = cl.user_info(msg.user_id).username
                            reply = f"@{username} {REPLY_MESSAGE}"
                            cl.direct_send(reply, thread_ids=[thread_id])
                            last_reply_time = time.time()
                            print(f"Replied to @{username} in group {thread_id}")
                        except Exception as e:
                            print(f"Error replying: {e}")
                        break  # Only one reply per thread

            time.sleep(5)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

auto_reply_all_groups()
