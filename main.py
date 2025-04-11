import time
from instagrapi import Client
from datetime import datetime, timedelta, timezone

USERNAME = "truequotesandstuff"
PASSWORD = "nobihuyaar@11"
REPLY_MESSAGE = "massage maat kar warna lynx ki maa shod ke feekkk dunga"

cl = Client()
cl.set_device({
    "app_version": "272.0.0.18.84",
    "android_version": 34,
    "android_release": "14",
    "dpi": "480dpi",
    "resolution": "1080x2400",
    "manufacturer": "infinix",
    "device": "Infinix-X6739",
    "model": "Infinix X6739",
    "cpu": "mt6893"
})
cl.login(USERNAME, PASSWORD)

last_reply_time = {}
blacklisted_threads = {}

def is_recent(msg):
    if not msg.timestamp: return False
    msg_time = msg.timestamp.astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - msg_time) < timedelta(seconds=60)

def auto_reply_all_groups():
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                title = thread.thread_title or "Unnamed"
                thread_id = thread.id

                if not thread.items or not thread.users or cl.user_id not in [u.pk for u in thread.users]:
                    print(f"[SKIPPED] Removed from group '{title}'")
                    continue

                if thread_id in blacklisted_threads:
                    continue

                try:
                    thread_data = cl.direct_thread(thread_id)
                    if not thread_data or not thread_data.messages:
                        continue

                    last_msg = thread_data.messages[0]

                    if getattr(last_msg, "type", "") == "xma_thread_name":
                        print(f"[SKIPPED] Name change event in '{title}'")
                        blacklisted_threads[thread_id] = time.time()
                        continue

                    if last_msg.user_id == cl.user_id or getattr(last_msg, "from_me", False):
                        print(f"[SKIPPED] Own message in '{title}'")
                        continue

                    if not is_recent(last_msg):
                        continue

                    if time.time() - last_reply_time.get(thread_id, 0) < 3:
                        continue

                    username = cl.user_info(last_msg.user_id).username
                    roast = f"@{username} {REPLY_MESSAGE}"
                    cl.direct_send(roast, thread_ids=[thread_id])
                    print(f"[REPLIED] To @{username} in '{title}'")
                    last_reply_time[thread_id] = time.time()

                except Exception as e:
                    print(f"[ERROR] Thread {title}: {e}")
                    continue

            time.sleep(3)

        except Exception as e:
            print(f"[MAIN LOOP ERROR] {e}")
            time.sleep(10)

auto_reply_all_groups()
