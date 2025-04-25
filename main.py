from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import logging
from datetime import datetime

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "/app/session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# ===== DEVICE SPOOFING =====
DEVICE_SETTINGS = {
    "app_version": "321.0.0.13.112",
    "android_version": 34,
    "android_release": "14",
    "dpi": "480dpi",
    "resolution": "1080x2400",
    "manufacturer": "infinix",
    "device": "Infinix-X6739",
    "model": "Infinix X6739",
    "cpu": "mt6893"
}
USER_AGENT = "Instagram 321.0.0.13.112 Android (34/14; 480dpi; 1080x2400; Infinix; Infinix-X6739; mt6893; en_US)"

# ===== SESSION MANAGEMENT =====
def validate_session():
    try:
        with open(SESSION_FILE, 'r') as f:
            json.load(f)
    except:
        reset_session_file()

def reset_session_file():
    with open(SESSION_FILE, 'w') as f:
        json.dump({}, f)

# ===== LOGIN FUNCTIONS =====
def login_client():
    validate_session()
    cl = Client()
    cl.set_device(DEVICE_SETTINGS)
    cl.set_user_agent(USER_AGENT)
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()
        logger.info("✅ Login successful (with session)")
        return cl
    except (LoginRequired, AttributeError):
        logger.warning("Session expired - fresh login")
        return fresh_login()
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return None

def fresh_login():
    cl = Client()
    cl.set_device(DEVICE_SETTINGS)
    cl.set_user_agent(USER_AGENT)
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        logger.info("✅ Fresh login successful and session saved")
        return cl
    except Exception as e:
        logger.error(f"Fresh login failed: {str(e)}")
        return None

# ===== GROUP MESSAGE HANDLING =====
def get_group_chats(cl):
    try:
        all_threads = cl.direct_threads()
        groups = [t for t in all_threads if len(t.users) > 1]
        logger.info(f"📦 Found {len(groups)} group chats")
        return groups
    except Exception as e:
        logger.error(f"Failed to get groups: {str(e)}")
        return []

def process_groups(cl):
    groups = get_group_chats(cl)
    if not groups:
        logger.warning("No groups found! Check if account is added to groups")
        return

    for group in groups:
        try:
            logger.info(f"💬 Processing group: {group.id}")
            messages = cl.direct_messages(thread_id=group.id, amount=5)
            if not messages:
                continue

            last_msg = messages[-1]
            if last_msg.user_id == cl.user_id:
                continue  # Avoid replying to self

            user = cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            cl.direct_send(text=reply_text, thread_ids=[group.id])
            logger.info(f"📩 Replied to @{user.username}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Group error: {str(e)}")
            time.sleep(5)

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting bot")
    client = None
    for _ in range(3):
        client = login_client()
        if client:
            break
        time.sleep(10)

    if not client:
        logger.error("❌ Permanent login failure")
        exit(1)

    while True:
        process_groups(client)
        logger.info("🔄 Next check in 30 seconds...")
        time.sleep(30)
