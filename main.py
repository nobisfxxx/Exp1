import random
from instagrapi import Client
from datetime import datetime, timedelta, timezone
import time
import json
import os

# --- CONFIG ---
USERNAME = "bot_check_hu"
PASSWORD = "nobilovestinglui"
REPLY_MESSAGE = "oii massage maat kar warna paradox ki maa shod ke feekkk dunga"
SESSION_FILE = "session_cookies.json"
BLACKLIST_FILE = "blacklist.json"
REPLY_INTERVAL = 3  # seconds
# ----------------

# Proxy list you provided
PROXIES = [
    '154.213.198.27:3128',
    '156.253.171.165:3128',
    '156.253.165.192:3128',
    '154.213.161.51:3128',
    '156.228.177.68:3128',
    '156.249.138.210:3128',
    '156.228.95.34:3128',
    '156.253.178.74:3128',
    '156.240.99.118:3128',
    '156.242.41.174:3128',
    '154.213.204.187:3128',
    '156.228.99.10:3128',
    '156.228.125.169:3128',
    '156.228.177.7:3128',
    '156.242.37.85:3128',
    '156.228.96.165:3128',
    '156.228.179.37:3128',
    '156.228.117.208:3128',
    '154.94.12.94:3128',
    '156.248.80.136:3128',
    '154.213.199.110:3128',
    '156.228.79.174:3128',
    '156.228.90.104:3128',
    '156.248.86.223:3128',
    '156.253.177.240:3128',
    '154.213.165.104:3128',
    '156.228.190.28:3128',
    '156.228.176.82:3128',
    '156.253.168.153:3128',
    '154.94.14.143:3128',
    '156.233.88.74:3128',
    '45.202.77.120:3128',
    '156.228.117.204:3128',
    '156.228.107.120:3128',
    '156.233.87.165:3128',
    '156.228.80.136:3128',
    '156.228.90.186:3128',
    '156.228.88.72:3128',
    '156.248.81.169:3128',
    '156.253.165.183:3128',
    '156.253.175.65:3128',
    '154.213.193.161:3128',
    '154.213.204.57:3128',
    '154.213.197.32:3128',
    '156.228.80.129:3128',
    '156.228.109.40:3128',
    '156.253.164.192:3128',
    '156.242.42.20:3128',
    '156.248.85.133:3128',
    '156.228.89.16:3128',
    '156.228.103.137:3128',
    '156.253.175.152:3128',
    '154.213.167.20:3128',
    '45.202.76.163:3128',
    '45.202.79.136:3128',
    '156.233.84.179:3128',
    '156.228.95.46:3128',
    '154.91.171.136:3128',
    '156.228.190.161:3128',
    '156.228.89.61:3128',
    '156.249.138.65:3128',
    '154.213.167.9:3128',
    '154.213.203.86:3128',
    '156.233.72.150:3128',
    '156.228.178.181:3128',
    '156.233.84.33:3128',
    '156.248.82.57:3128',
    '156.233.88.232:3128',
    '156.233.74.142:3128',
    '156.253.177.129:3128',
    '156.233.90.59:3128',
    '156.228.89.177:3128',
    '154.213.162.153:3128',
    '156.228.103.64:3128',
    '156.233.91.109:3128',
    '156.228.189.1:3128',
    '156.248.82.122:3128',
    '156.228.84.28:3128',
    '154.213.160.121:3128',
    '156.240.99.115:3128',
    '45.202.79.158:3128',
    '156.249.59.130:3128',
    '45.202.77.138:3128',
    '156.233.75.77:3128',
    '156.228.92.196:3128',
    '154.213.163.42:3128',
    '156.249.60.223:3128',
    '154.213.202.205:3128',
    '156.233.92.9:3128',
    '156.228.181.192:3128',
    '156.228.103.52:3128',
    '156.242.39.144:3128',
    '156.228.88.51:3128',
    '156.253.179.177:3128',
    '156.242.45.53:3128',
    '156.228.176.218:3128',
    '156.228.119.146:3128',
    '156.233.91.238:3128',
    '156.228.99.121:3128',
    '154.213.167.171:3128',
]

# --- CONFIG ---
USERNAME = "bot_check_hu"
PASSWORD = "nobilovestinglui"
SESSION_FILE = "session_cookies.json"
BLACKLIST_FILE = "blacklist.json"
REPLY_MESSAGE = "oii massage maat kar warna paradox ki maa shod ke feekkk dunga"
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

# Set a proxy
def set_proxy():
    proxy = random.choice(PROXIES)  # Randomly choose a proxy from the list
    print(f"Using proxy: {proxy}")
    cl.set_proxy(f'http://{proxy}')

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
            set_proxy()  # Set proxy at the start of the loop
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
                    thread_data = cl.direct_messages(thread_id)
                    last_message = thread_data[0]
                except Exception:
                    continue

                if time.time() - last_reply_time >= REPLY_INTERVAL and 'group name changed' not in last_message.text.lower():
                    if should_blacklist_group(thread):
                        blacklisted_threads.add(thread_id)
                        with open(BLACKLIST_FILE, 'w') as f:
                            json.dump(list(blacklisted_threads), f)
                        print(f"Blacklisted group {thread_id} due to frequent name changes.")
                    else:
                        cl.direct_send(REPLY_MESSAGE, thread_id)
                        last_reply_time = time.time()

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# Run the bot
auto_reply_all_groups()
