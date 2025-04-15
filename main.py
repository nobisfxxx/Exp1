import os
import json
import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

USERNAME = "rdp_god_hu"
PASSWORD = "nobihuyaarr@11"
SESSION_FILE = "session.json"

ROAST_MESSAGES = [
    "bhai tu rehne de, tera IQ room temperature se bhi kam hai.",
    "jitni baar tu bolta hai, utni baar embarrassment hoti hai Indian education system ko.",
    "tera logic dekh ke calculator bhi suicide kar le.",
    "chal na, tujhme aur Google translate me zyada fark nahi.",
    "tu chup kar, warna tera browser history sabke saamne daal dunga.",
    "tera reply padke lagta hai ki evolution ne break le liya tha.",
    "teri soch ka GPS signal lost dikha raha hai.",
    "tu rehne de bhai, tere jaise logon ko autocorrect bhi ignore karta hai.",
    "tu zyada bolta hai, aur samajh kamta hai.",
    "beta tu abhi training wheels pe chal raha hai, formula 1 ke sapne mat dekh.",
    # Add more roast messages here if needed
]

def save_session(cl):
    with open(SESSION_FILE, "w") as f:
        json.dump(cl.get_settings(), f)

def load_session(cl):
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            cl.set_settings(json.load(f))
        try:
            cl.get_timeline_feed()
            print("[LOGIN SUCCESS] Session loaded.")
            return True
        except:
            print("[SESSION INVALID] Login required.")
    return False

def login():
    cl = Client()
    cl.delay_range = [2, 4]
    
    if load_session(cl):
        return cl

    try:
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()
        save_session(cl)
        print(f"[LOGIN SUCCESS] Logged in as {USERNAME}")
    except Exception as e:
        print(f"[LOGIN FAILED] {e}")
        exit()
    return cl

def get_my_user_id(cl):
    try:
        user = cl.user_info_by_username(USERNAME)
        return user.pk
    except Exception as e:
        print(f"[ERROR] Could not fetch user id: {e}")
        return None

def get_recent_messages(cl):
    try:
        return cl.direct_threads()
    except LoginRequired:
        print("[DEBUG] Session expired.")
        return []
    except Exception as e:
        print(f"[ERROR getting threads] {e}")
        return []

def reply_to_group_messages(cl, my_user_id):
    print("[BOT ACTIVE] Forced reply mode (no reply_to)...")
    while True:
        threads = get_recent_messages(cl)
        for thread in threads:
            if not thread.is_group:
                continue

            try:
                updated_thread = cl.direct_thread(thread.id)
                last_msg: DirectMessage = updated_thread.messages[0]

                if last_msg.user_id == my_user_id:
                    continue  # skip own messages

                user_info = cl.user_info(last_msg.user_id)
                roast = random.choice(ROAST_MESSAGES)
                reply = f"@{user_info.username} {roast}"

                cl.direct_send(text=reply, thread_ids=[thread.id])
                print(f"[REPLIED] To @{user_info.username}: {roast}")

            except Exception as e:
                print(f"[ERROR sending reply] {e}")
        time.sleep(5)

def main():
    cl = login()
    my_user_id = get_my_user_id(cl)
    if my_user_id:
        reply_to_group_messages(cl, my_user_id)

if __name__ == "__main__":
    main()
