import os
import json
from time import sleep
from instagrapi import Client
from instagrapi.types import StoryMention

USERNAME = "lynx_chod_hu"
PASSWORD = "nobihuyaar@111"
DEVICE_FILE = "device.json"
SESSION_FILE = "session.json"

def save_session(client):
    with open(DEVICE_FILE, "w") as f:
        json.dump(client.get_settings(), f)

def login():
    cl = Client()

    if os.path.exists(DEVICE_FILE):
        with open(DEVICE_FILE) as f:
            cl.set_settings(json.load(f))

    try:
        cl.load_settings(SESSION_FILE)
        cl.get_timeline_feed()
        print("[+] Logged in with saved session")
    except Exception:
        print("[-] Session invalid, logging in again...")
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        save_session(cl)
        print("[+] Logged in successfully")
    
    return cl

# Initialize client
cl = login()

def send_to_all_groups(message):
    me = cl.user_id
    threads = cl.direct_threads()

    for thread in threads:
        if not thread.is_group:
            continue
        if me not in [u.pk for u in thread.users]:
            print(f"[-] Skipping {thread.thread_title} (not a participant)")
            continue

        mentions = []
        for user in thread.users:
            if user.pk != me:
                mention_text = f"@{user.username}"
                mentions.append(mention_text)

        full_message = message + "\n\n" + " ".join(mentions)

        try:
            cl.direct_send(full_message, [thread.id])
            print(f"[+] Sent to: {thread.thread_title}")
            sleep(3)
        except Exception as e:
            print(f"[-] Failed to send to {thread.thread_title}: {e}")

# Customize your message below
send_to_all_groups("oiii massage maat kar warna nobi aa jaega")
