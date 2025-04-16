import os
import time
import random
from datetime import datetime, timezone, timedelta
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

# Your Instagram credentials
USERNAME = "lynx_chod_hu"
PASSWORD = "nobihuyaar@111"

# Custom roast replies
ROASTS = [
    "Bhai tu rehne de, tera IQ room temperature se bhi kam hai.",
    "Jitni baar tu bolta hai, utni baar embarrassment hoti hai education system ko.",
    "Tera logic dekh ke calculator bhi crash ho jaye.",
    "Tu chup kar, warna Google bhi ignore kar dega.",
    "Bhai tu offline ho ja, tera net zyada samajhdar hai."
]

# Keep track of last replied message ID per thread
LAST_REPLIED = {}

def login():
    cl = Client()
    try:
        cl.login(USERNAME, PASSWORD)
        print("[+] Logged in successfully")
    except Exception as e:
        print("[-] Login failed:", e)
        exit()
    return cl

def reply_to_groups(cl):
    while True:
        try:
            threads = cl.direct_threads(amount=10)
            for thread in threads:
                if not thread.is_group or not thread.users:
                    continue

                # Skip if bot is not in the group anymore
                if cl.user_id not in [u.pk for u in thread.users]:
                    continue

                if not thread.messages:
                    continue

                last_msg = thread.messages[0]
                msg_time = last_msg.timestamp.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)

                # Only reply to fresh messages within 60 seconds
                if (now - msg_time).total_seconds() > 60:
                    continue

                # Skip if already replied to this message
                if LAST_REPLIED.get(thread.id) == last_msg.id:
                    continue

                # Skip own messages
                if last_msg.user_id == cl.user_id:
                    continue

                roast = random.choice(ROASTS)
                cl.direct_send(roast, [thread.id])
                LAST_REPLIED[thread.id] = last_msg.id
                print(f"[+] Replied in thread {thread.id}: {roast}")
                time.sleep(3)

        except LoginRequired:
            print("[-] Session expired. Re-logging in...")
            cl = login()
        except Exception as e:
            print("[-] Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    client = login()
    reply_to_groups(client)
