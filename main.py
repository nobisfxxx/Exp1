import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

USERNAME = "nobi.bot"
PASSWORD = "nobihuyaar@11"

ROAST_MESSAGES = [
    "bol Samay or karan ki mkb.",
    "Samay or karan ki mkb me nobi.",
    "tera logic dekh ke calculator bhi suicide kar le.",
    "chal Samay or karan, tujhme aur Google translate me zyada fark nahi.",
    "Samay or karan chup kar, warna tera browser history sabke saamne daal dunga.",
    "Samay or karan reply padke lagta hai ki evolution ne break le liya tha.",
    "Samay or karan soch ka GPS signal lost dikha raha hai.",
    "Samay or karan rehne de bhai, tere jaise logon ko autocorrect bhi ignore karta hai.",
    "Samay or karan zyada bolta hai, aur samajh kamta hai.",
    "Samay or karan abasi abhi training wheels pe chal raha hai, formula 1 ke sapne mat dekh.",
    # Add more if you want
]

def safe_login():
    cl = Client()
    cl.delay_range = [2, 4]
    try:
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()  # confirms login is good
        print(f"[LOGIN SUCCESS] Logged in as {USERNAME}")
        return cl
    except Exception as e:
        print(f"[LOGIN FAILED] {e}")
        return None

def get_recent_threads(cl):
    try:
        threads = cl.direct_threads()
        if not threads:
            raise ValueError("No threads returned.")
        return threads
    except LoginRequired:
        print("[SESSION EXPIRED] Trying relogin...")
        try:
            cl.relogin()
        except Exception as e:
            print(f"[RELOGIN FAILED] {e}")
            return []
        return cl.direct_threads()
    except Exception as e:
        print(f"[ERROR getting threads] {e}")
        return []

def reply_to_group_messages(cl):
    print("[BOT ACTIVE] Safe mode running...")
    my_user_id = cl.user_id

    while True:
        threads = get_recent_threads(cl)
        if not threads:
            print("[DEBUG] No threads fetched. Sleeping...")
            time.sleep(2)
            continue

        for thread in threads:
            if not thread.is_group:
                continue

            try:
                updated_thread = cl.direct_thread(thread.id)
                last_msg: DirectMessage = updated_thread.messages[0]

                if last_msg.user_id == my_user_id:
                    continue  # prevent self-reply

                user_info = cl.user_info(last_msg.user_id)
                roast = random.choice(ROAST_MESSAGES)
                reply = f"@{user_info.username} {roast}"

                cl.direct_send(text=reply, thread_ids=[thread.id])
                print(f"[REPLIED] To @{user_info.username}: {roast}")
            except Exception as e:
                print(f"[ERROR sending reply] {e}")

        time.sleep(2)  # Safe delay between checks

def main():
    cl = safe_login()
    if cl:
        reply_to_group_messages(cl)
    else:
        print("[FATAL] Could not login. Exiting.")

if __name__ == "__main__":
    main()
