from instagrapi import Client
import time
from datetime import datetime, timezone

# --- CONFIG ---
USERNAME = "truequotesandstuff"
PASSWORD = "nobihuyaar@11"
REPLY_MESSAGE = "oii massage maat kar warna nobi aake hate dene wallon ki kaa shod dega"
REPLY_DELAY = 3  # seconds between replies per group
# --------------------------------

cl = Client()

# Set spoofed device
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

def is_recent(msg):
    if msg.timestamp:
        now = datetime.now(timezone.utc)
        return (now - msg.timestamp).total_seconds() <= 60
    return False

def is_name_change_event(msg):
    return msg.type in ['action_log', 'xma', 'animated_media', 'reel_share'] or 'change' in str(msg).lower()

def auto_reply_groups():
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                thread_id = thread.id

                if not thread.is_group or not thread.thread_title:
                    continue

                # Skip if bot is no longer a participant
                if cl.user_id not in [u.pk for u in thread.users]:
                    print(f"[SKIPPED] Removed from group '{thread.thread_title}'")
                    continue

                try:
                    thread_data = cl.direct_thread(thread_id)
                    messages = thread_data.messages
                    if not messages:
                        continue
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
                    continue

                for msg in reversed(messages):
                    if msg.user_id != cl.user_id and is_recent(msg):
                        if is_name_change_event(msg):
                            print(f"[SKIPPED] Group rename in '{thread.thread_title}'")
                            break

                        try:
                            username = cl.user_info(msg.user_id).username
                            reply = f"@{username} {REPLY_MESSAGE}"

                            now = time.time()
                            if thread_id in last_reply_time and now - last_reply_time[thread_id] < REPLY_DELAY:
                                break

                            cl.direct_send(reply, thread_ids=[thread_id])
                            last_reply_time[thread_id] = now
                            print(f"[REPLIED] to @{username} in '{thread.thread_title}'")
                        except Exception as e:
                            print(f"Reply error: {e}")
                        break
            time.sleep(5)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    auto_reply_groups()
