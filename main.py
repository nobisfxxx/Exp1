import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

USERNAME = "lynx_chod_hu"
PASSWORD = "babytingting"

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
]

def login():
    cl = Client()
    cl.delay_range = [1, 3]
    try:
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()  # helps set user_id
        print(f"[LOGIN SUCCESS] Logged in as {USERNAME}")
    except Exception as e:
        print(f"[LOGIN FAILED] {e}")
        exit()
    return cl

def get_recent_messages(cl):
    try:
        return cl.direct_threads()
    except LoginRequired:
        print("[DEBUG] Session expired. Re-logging...")
        cl.login(USERNAME, PASSWORD)
        return cl.direct_threads()
    except Exception as e:
        print(f"[ERROR getting threads] {e}")
        return []

def reply_to_group_messages(cl):
    print("[BOT ACTIVE] Forced reply mode (no reply_to)...")
    my_user_id = cl.user_id  # fetch after login to avoid replying to self

    while True:
        threads = get_recent_messages(cl)
        for thread in threads:
            if not thread.is_group:
                continue

            try:
                updated_thread = cl.direct_thread(thread.id)  # ensure fresh messages
                last_msg: DirectMessage = updated_thread.messages[0]

                if last_msg.user_id == my_user_id:
                    continue  # skip own messages

                user_info = cl.user_info(last_msg.user_id)
                roast = random.choice(ROAST_MESSAGES)
                reply = f"@{user_info.username} {roast}"

                cl.direct_send(
                    text=reply,
                    thread_ids=[thread.id]
                )
                print(f"[REPLIED] To @{user_info.username}: {roast}")

            except Exception as e:
                print(f"[ERROR sending reply] {e}")
        time.sleep(5)

def main():
    cl = login()
    reply_to_group_messages(cl)

if __name__ == "__main__":
    main()
