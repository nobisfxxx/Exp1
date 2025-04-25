import time
import random
import logging
from instagrapi import Client
from config import DEVICE_SETTINGS, USER_AGENT, SESSION_ID
from roasts import ROAST_MESSAGES

cl = Client()
cl.set_device(DEVICE_SETTINGS)
cl.set_user_agent(USER_AGENT)
cl.login_by_sessionid(SESSION_ID)

logging.basicConfig(level=logging.INFO)
last_replied = {}

def safe_username(user):
    return user.username or f"id_{user.pk}"

def should_reply(thread_id):
    now = time.time()
    if thread_id not in last_replied or (now - last_replied[thread_id]) > 3:
        last_replied[thread_id] = now
        return True
    return False

while True:
    try:
        threads = cl.direct_threads()
        for thread in threads:
            if not thread.users or not thread.items:
                continue

            if not thread.thread_title or not thread.is_group:
                continue  # skip DMs or inactive

            last_item = thread.items[0]
            if last_item.user_id == cl.user_id:
                continue  # skip self replies

            timestamp = last_item.timestamp.timestamp()
            if time.time() - timestamp > 60:
                continue  # old message

            if not should_reply(thread.id):
                continue

            roast = random.choice(ROAST_MESSAGES)
            sender = safe_username(last_item.user)
            message = f"@{sender} {roast}"

            cl.direct_answer(thread.id, message)
            logging.info(f"Roasted @{sender} in {thread.thread_title}")

        time.sleep(5)

    except Exception as e:
        logging.error(f"Error: {e}")
        time.sleep(10)
