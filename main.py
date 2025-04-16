import os
import json
import random
import time
from datetime import datetime, timedelta, timezone
from instagrapi import Client

# Set environment-based login
USERNAME = os.environ.get("IG_USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD")

# File paths (Railway-safe)
SESSION_FILE = "/tmp/session.json"
REPLY_TRACK_FILE = "/tmp/replied_messages.json"
STOP_FILE = "/tmp/stopped_threads.json"

# Message bank
REPLY_MESSAGES = [
    "bhai tu rehne de, tera IQ room temperature se bhi kam hai.",
    "jitni baar tu bolta hai, utni baar embarrassment hoti hai Indian education system ko.",
    "tera logic dekh ke calculator bhi suicide kar le.",
    "chal na, tujhme aur Google translate me zyada fark nahi.",
    "tu chup kar, warna tera browser history sabke saamne daal dunga.",
    "tera reply padke lagta hai ki evolution ne break le liya tha.",
    "teri soch ka GPS signal lost dikha raha hai.",
    "tu rehne de bhai, tere jaise logon ko autocorrect bhi ignore karta hai.",
    "tu zyada bolta hai, aur samajh kamta hai.",
    "beta tu abhi training wheels pe chal raha hai, formula 1 ke sapne mat dekh."
]

# Initialize client
cl = Client()

# Load replied message IDs
try:
    with open(REPLY_TRACK_FILE, "r") as f:
        replied_messages = json.load(f)
except:
    replied_messages = {}

# Load stopped threads
try:
    with open(STOP_FILE, "r") as f:
        stopped_threads = json.load(f)
except:
    stopped_threads = []

def save_replied_messages():
    with open(REPLY_TRACK_FILE, "w") as f:
        json.dump(replied_messages, f)

def save_stopped_threads():
    with open(STOP_FILE, "w") as f:
        json.dump(stopped_threads, f)

def login():
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
            return
        except:
            pass
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)

def auto_reply_all_groups():
    while True:
        try:
            threads = cl.direct_threads(amount=20)
            for thread in threads:
                if not thread.users or thread.thread_id in stopped_threads:
                    continue
                messages = cl.direct_messages(thread.id, amount=10)
                for message in messages[::-1]:
                    # Skip if too old
                    if datetime.now(timezone.utc) - message.timestamp > timedelta(seconds=60):
                        continue
                    if message.id in replied_messages.get(thread.id, []):
                        continue
                    if message.user_id == cl.user_id:
                        continue

                    text = random.choice(REPLY_MESSAGES)
                    cl.direct_send(text, [thread.id], reply_to_message_id=message.id)
                    print(f"[+] Replied in thread {thread.id} to {message.user_id}")
                    replied_messages.setdefault(thread.id, []).append(message.id)
                    save_replied_messages()
                    time.sleep(3)
        except Exception as e:
            print(f"[!] Error: {e}. Retrying in 15s...")
            time.sleep(15)

# Login and run
login()
auto_reply_all_groups()
