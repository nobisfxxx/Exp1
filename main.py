import random
from instagrapi import Client
import json
import time
import os

# --- CONFIG ---
USERNAME = "bot_check_hu"
PASSWORD = "nobilovestinglui"
SESSION_FILE = "session_cookies.json"
REPLY_MESSAGE = "oii massage maat kar warna paradox ki maa shod ke feekkk dunga"
REPLY_INTERVAL = 3  # seconds
PROXIES = [
    '154.213.198.27:3128',
    '156.253.171.165:3128',
    # Add more proxies here
]
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
def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            # Test the session with a simple request
            cl.get_timeline_feed()
            print("Logged in using saved session.")
        except Exception as e:
            print(f"Session load failed: {e}")
            # Session failed to load, need to re-login
            re_login()
    else:
        # No session file, login directly
        re_login()

# Login method
def re_login():
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("Logged in successfully and session saved.")
    except Exception as e:
        print(f"Login failed: {e}")

# Proxy and session management
def auto_reply_all_groups():
    global last_reply_time
    last_reply_time = 0  # Initialize last_reply_time
    while True:
        try:
            set_proxy()  # Set proxy at the start of the loop
            threads = cl.direct_threads()
            for thread in threads:
                if thread.inviter is None or len(thread.users) <= 2:
                    continue

                # Skip blacklisted threads or already replied threads
                thread_id = thread.id
                try:
                    thread_data = cl.direct_messages(thread_id)
                    last_message = thread_data[0]
                except Exception:
                    continue

                if time.time() - last_reply_time >= REPLY_INTERVAL and 'group name changed' not in last_message.text.lower():
                    cl.direct_send(REPLY_MESSAGE, thread_id)
                    last_reply_time = time.time()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# Initialize session and run the bot
load_session()
auto_reply_all_groups()
