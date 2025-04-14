import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

# Make sure your username and password are correctly defined
USERNAME = "bot_check_hu"
PASSWORD = "nobilovestinglui"

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
        # Ensure you are passing both username and password
        cl.login(USERNAME, PASSWORD)
        print("[LOGIN SUCCESS]")
    except Exception as e:
        print(f"[LOGIN FAILED] {e}")
        exit()
    return cl

def get_recent_messages(cl):
    try:
        threads = cl.direct_threads()
        return threads
    except LoginRequired:
        print("[DEBUG] Session expired. Re-logging...")
        cl.login(USERNAME, PASSWORD)
        return cl.direct_threads()
    except Exception as e:
        print(f"[ERROR getting threads] {e}")
        return []

def reply_to_group_messages(cl):
    print("[BOT ACTIVE] FORCED reply mode testing (no reply_to)...")
    while True:
        threads = get_recent_messages(cl)
        for thread in threads:
            if not thread.is_group:
                continue

            last_msg: DirectMessage = thread.messages[0]
            if last_msg.user_id == cl.user_id:
                continue  # skip if the bot sent it

            try:
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
