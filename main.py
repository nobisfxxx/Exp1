import random
import time
import json
import os
from instagrapi import Client
from itertools import cycle

# --- CONFIG ---
USERNAME = "rumeyaaakdemir5055"
PASSWORD = "nobihuyaar@11"

DEFAULT_REPLY_MESSAGE = "oii massage maat kar warna lynx ki maa shod ke feekkk dunga"
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work weelll?.. If not make changes to the script.. till then boii boii boss"

STOP_COMMAND = "stop the bot on this gc"
RESUME_COMMAND = "resume the bot on this gc"

PASSWORD_REQUEST = "Okay, boss. What's the password?"
VALID_PASSWORD = "17092004"

CONFIRM_STOP = "Bot stopped for this group. Catch ya later, boss!"
WRONG_PASSWORD = "Wrong password, boss. Try again or stay roasted."
CONFIRM_RESUME = "Bot resumed for this group. I’m back in action, boss!"

STOP_FILE = "stopped_threads.json"
REPLY_TRACK_FILE = "replied_messages.json"

PROXIES = [
    "http://103.67.91.50:8081"
]

# Initialize the client
cl = Client()

# Load stopped threads
if os.path.exists(STOP_FILE):
    with open(STOP_FILE, "r") as f:
        stopped_threads = set(json.load(f))
else:
    stopped_threads = set()

# Load replied messages
if os.path.exists(REPLY_TRACK_FILE):
    with open(REPLY_TRACK_FILE, "r") as f:
        last_replied = json.load(f)
else:
    last_replied = {}

awaiting_password = {}

def save_stopped_threads():
    with open(STOP_FILE, "w") as f:
        json.dump(list(stopped_threads), f)

def save_last_replied():
    with open(REPLY_TRACK_FILE, "w") as f:
        json.dump(last_replied, f)

def rotate_proxies():
    return cycle(PROXIES)

def login_with_proxy(proxy):
    try:
        print(f"Attempting login with proxy: {proxy}")
        cl.set_proxy(proxy)
        cl.login(USERNAME, PASSWORD)
        print(f"Logged in successfully using proxy {proxy}")
    except Exception as e:
        print(f"Error during login with proxy {proxy}: {e}")
        return False
    return True

def auto_reply_all_groups():
    proxy_cycle = rotate_proxies()
    while True:
        try:
            # Try login using proxies, rotate on failure
            if not login_with_proxy(next(proxy_cycle)):
                print("Login failed, retrying with another proxy...")
                time.sleep(5)
                continue

            threads = cl.direct_threads()
            for thread in threads:
                if thread.inviter is None or len(thread.users) <= 2:
                    continue

                thread_id = thread.id
                try:
                    thread_data = cl.direct_thread(thread_id)
                    if thread_data is None:
                        continue
                    messages = thread_data.messages
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
                    continue

                for msg in reversed(messages):
                    if msg.user_id == cl.user_id:
                        continue

                    message_id = str(msg.id)
                    text = msg.text.lower()
                    username = cl.user_info(msg.user_id).username

                    if last_replied.get(thread_id) == message_id:
                        break

                    try:
                        if thread_id in awaiting_password:
                            mode = awaiting_password[thread_id]
                            if VALID_PASSWORD in text:
                                if mode == "stop":
                                    cl.direct_send(CONFIRM_STOP, thread_ids=[thread_id])
                                    stopped_threads.add(thread_id)
                                    save_stopped_threads()
                                    print(f"Bot stopped in {thread_id}")
                                elif mode == "resume":
                                    if thread_id in stopped_threads:
                                        stopped_threads.remove(thread_id)
                                        cl.direct_send(CONFIRM_RESUME, thread_ids=[thread_id])
                                        save_stopped_threads()
                                        print(f"Bot resumed in {thread_id}")
                                    awaiting_password.pop(thread_id)
                            else:
                                cl.direct_send(WRONG_PASSWORD, thread_ids=[thread_id])
                            last_replied[thread_id] = message_id
                            save_last_replied()
                            break

                        if STOP_COMMAND in text:
                            cl.direct_send(PASSWORD_REQUEST, thread_ids=[thread_id])
                            awaiting_password[thread_id] = "stop"
                            last_replied[thread_id] = message_id
                            save_last_replied()
                            break

                        if RESUME_COMMAND in text:
                            cl.direct_send(PASSWORD_REQUEST, thread_ids=[thread_id])
                            awaiting_password[thread_id] = "resume"
                            last_replied[thread_id] = message_id
                            save_last_replied()
                            break

                        if thread_id in stopped_threads:
                            break

                        if TRIGGER_PHRASE in text:
                            cl.direct_send(TRIGGER_RESPONSE, thread_ids=[thread_id])
                            print(f"Triggered response to @{username}")
                        else:
                            reply = f"@{username} {DEFAULT_REPLY_MESSAGE}"
                            cl.direct_send(reply, thread_ids=[thread_id])
                            print(f"Roasted @{username}")

                        last_replied[thread_id] = message_id
                        save_last_replied()
                    except Exception as e:
                        print(f"Error replying in thread {thread_id}: {e}")
                    break  # only one reply per thread per cycle
            time.sleep(2)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(2)

auto_reply_all_groups()
