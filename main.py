import os
import time
from datetime import datetime, timezone, timedelta
from instagrapi import Client

REPLY_MESSAGE = "oii massage maat kar warna tere maa shod ke feekkk dunga"

DEVICE = {
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
cl.set_device(DEVICE)

# Fetching Instagram credentials from environment variables
USERNAME = os.environ.get("bot_check_hu")
PASSWORD = os.environ.get("nobilovestinglui")

# Login to Instagram using credentials from environment variables
cl.login(USERNAME, PASSWORD)

last_reply_time = {}
blacklisted_threads = {}

def is_recent(msg):
    if not msg.timestamp:
        return False
    now = datetime.now(timezone.utc)
    return (now - msg.timestamp) < timedelta(seconds=60)

def is_group_rename(msg):
    return getattr(msg, "item_type", "") == "group_title"

def auto_reply_all_groups():
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if thread.inviter is None or len(thread.users) <= 2:
                    continue
                thread_id = thread.id

                if blacklisted_threads.get(thread_id, 0) >= 3:
                    print(f"[BLACKLISTED] {thread.thread_title}")
                    continue

                try:
                    thread_data = cl.direct_thread(thread_id)
                    if not thread_data or not thread_data.messages:
                        continue

                    if not any(u.pk == cl.user_id for u in thread_data.users):
                        print(f"[SKIPPED] Removed from group '{thread.thread_title}'")
                        continue

                    messages = thread_data.messages
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
                    continue

                for msg in reversed(messages):
                    if not is_recent(msg) or msg.user_id == cl.user_id:
                        continue
                    if is_group_rename(msg):
                        blacklisted_threads[thread_id] = blacklisted_threads.get(thread_id, 0) + 1
                        print(f"[SKIPPED] Rename detected in '{thread.thread_title}'")
                        continue

                    last_time = last_reply_time.get(thread_id, 0)
                    if time.time() - last_time < 2.5:
                        continue

                    try:
                        sender = cl.user_info(msg.user_id).username
                        reply = f"@{sender} {REPLY_MESSAGE}"
                        cl.direct_send(reply, thread_ids=[thread_id])
                        print(f"Replied to @{sender} in '{thread.thread_title}'")
                        last_reply_time[thread_id] = time.time()
                    except Exception as e:
                        print(f"Error replying: {e}")
                    break
            time.sleep(5)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    auto_reply_all_groups()
