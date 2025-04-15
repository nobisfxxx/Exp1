import time
import random
import json
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

USERNAME = "lynx_chod_hu"
PASSWORD = "babytingting"
COOKIE_PATH = "login_cookies.json"  # Path to store the login cookies

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
    # Add more roast messages here
]

def login_with_cookies():
    cl = Client()
    try:
        # Check if cookies exist and load them
        with open(COOKIE_PATH, "r") as cookie_file:
            cookies = json.load(cookie_file)
            cl.set_cookies(cookies)
            cl.get_timeline_feed()  # Test if the session is valid
            print(f"[LOGIN SUCCESS] Logged in using cookies as {USERNAME}")
            return cl
    except Exception as e:
        print(f"[LOGIN FAILED] Cookies not valid or not found. Logging in with credentials: {e}")
        cl.login(USERNAME, PASSWORD)
        # Save cookies after the first successful login
        with open(COOKIE_PATH, "w") as cookie_file:
            json.dump(cl.cookies, cookie_file)
        print(f"[LOGIN SUCCESS] Logged in as {USERNAME}")
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

def retry_on_error(func, retries=5, delay=5):
    """Retries a function on 500 errors with exponential backoff"""
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"[ERROR] {e}, Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    print("[ERROR] Max retries exceeded.")
    return None

def reply_to_group_messages(cl):
    print("[BOT ACTIVE] Forced reply mode (no reply_to)...")
    my_user_id = cl.user_id  # fetch after login to avoid replying to self

    while True:
        threads = retry_on_error(get_recent_messages, retries=3, delay=5)
        if threads is None:
            print("[ERROR] Failed to get threads, skipping this loop...")
            continue
        
        for thread in threads:
            if not thread.is_group:
                continue

            try:
                updated_thread = retry_on_error(lambda: cl.direct_thread(thread.id), retries=3, delay=5)
                if updated_thread is None:
                    continue  # Skip if fetching thread failed
                
                last_msg: DirectMessage = updated_thread.messages[0]

                if last_msg.user_id == my_user_id:
                    continue  # skip own messages

                user_info = cl.user_info(last_msg.user_id)
                roast = random.choice(ROAST_MESSAGES)
                reply = f"@{user_info.username} {roast}"

                retry_on_error(lambda: cl.direct_send(
                    text=reply,
                    thread_ids=[thread.id]
                ), retries=3, delay=5)
                print(f"[REPLIED] To @{user_info.username}: {roast}")

            except Exception as e:
                print(f"[ERROR sending reply] {e}")
        time.sleep(5)

def main():
    cl = login_with_cookies()
    reply_to_group_messages(cl)

if __name__ == "__main__":
    main()
