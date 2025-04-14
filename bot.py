from instagrapi import Client
from datetime import datetime, timedelta, timezone
import json, time, os
from roast_messages import ROASTS
from cy_device_spoofing import get_device  # Cython optimized
import pytz

# Load cookies
with open("cookies.json", "r") as f:
    cookies = json.load(f)

cl = Client()
cl.set_device(get_device())
cl.set_cookie(cookies)

try:
    cl.login_by_sessionid(cookies["sessionid"])
except Exception:
    print("Session invalid. Exiting.")
    exit()

# Settings
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work weelll?.."
DEFAULT_REPLY = "oii massage maat kar warna lynx ki maa shod ke feekkk dunga"
STOP_COMMAND = "stop the bot on this gc"
RESUME_COMMAND = "resume the bot on this gc"
VALID_PASSWORD = "17092004"

group_status = {}
last_reply_time = {}

def reply_to_group(thread_id, msg_id, text):
    try:
        cl.direct_answer(thread_id, msg_id, text)
    except Exception as e:
        print(f"[!] Reply failed: {e}")

while True:
    try:
        threads = cl.direct_threads()
        for thread in threads:
            if not thread.is_group or thread.thread_id in group_status and not group_status[thread.thread_id]:
                continue
            if not thread.items:
                continue

            last_msg = thread.items[0]
            if last_msg.user_id == cl.user_id:
                continue

            msg_time = last_msg.timestamp.astimezone(timezone.utc)
            now = datetime.now(timezone.utc)
            if now - msg_time > timedelta(seconds=60):
                continue

            sender = cl.user_info(last_msg.user_id).username
            text = last_msg.text or ""

            if text == STOP_COMMAND:
                reply_to_group(thread.thread_id, last_msg.id, "Okay, bot stopped. Password?")
                group_status[thread.thread_id] = False
                continue
            elif text == RESUME_COMMAND:
                reply_to_group(thread.thread_id, last_msg.id, "Bot resumed, boss.")
                group_status[thread.thread_id] = True
                continue
            elif not group_status.get(thread.thread_id, True):
                continue

            if TRIGGER_PHRASE in text:
                reply_to_group(thread.thread_id, last_msg.id, TRIGGER_RESPONSE)
            else:
                if time.time() - last_reply_time.get(thread.thread_id, 0) < 3:
                    continue
                roast = f"@{sender} " + random.choice(ROASTS)
                reply_to_group(thread.thread_id, last_msg.id, roast)
                last_reply_time[thread.thread_id] = time.time()

    except Exception as e:
        print(f"[!] Error loop: {e}")
        time.sleep(5)
