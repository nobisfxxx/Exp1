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

# ===== SESSION MANAGEMENT =====
def validate_session():
    """Ensure session file structure is valid"""
    required_keys = ["cookies", "last_login", "device_settings", "user_agent"]
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            if not all(key in data for key in required_keys):
                raise ValueError("Invalid session structure")
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        logger.warning("Resetting corrupted session file")
        reset_session_file()

def reset_session_file():
    """Create fresh valid session structure"""
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": {
                "app_version": "219.0.0.12.117",
                "android_version": 25,
                "android_release": "7.1.2"
            },
            "user_agent": "Instagram 219.0.0.12.117 Android"
        }, f)

# ===== CORE FUNCTIONALITY =====
def login_client():
    """Robust login with session recovery"""
    validate_session()
    
    cl = Client()
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()  # Verify session
        logger.info("✅ Login successful")
        return cl
    except (LoginRequired, AttributeError):
        logger.warning("Session expired - fresh login")
        return fresh_login()
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return None

def fresh_login():
    """Force new login and session creation"""
    cl = Client()
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        return cl
    except Exception as e:
        logger.error(f"Fresh login failed: {str(e)}")
        return None

def get_group_chats(cl):
    """Get group chats by checking participant count"""
    try:
        all_threads = cl.direct_threads()
        groups = [t for t in all_threads if len(t.users) > 1]
        logger.info(f"📦 Found {len(groups)} group chats")
        return groups
    except Exception as e:
        logger.error(f"Failed to get groups: {str(e)}")
        return []

def process_groups(cl):
    """Process messages in all group chats"""
    groups = get_group_chats(cl)
    if not groups:
        logger.warning("No groups found! Check if account is added to groups")
        return

    for group in groups:
        try:
            logger.info(f"💬 Processing group: {group.id}")
            
            # Check if the bot is still a participant
            if cl.user_id not in [user.pk for user in group.users]:
                logger.info(f"❌ Skipping group {group.id} as bot is no longer a participant")
                continue  # Skip this group if bot is not a participant

            # Get last 5 messages
            messages = cl.direct_messages(thread_id=group.id, amount=5)
            if not messages:
                continue
                
            last_msg = messages[-1]
            if last_msg.user_id == cl.user_id:
                continue  # Skip own messages
                
            # Send reply (version-compatible)
            user = cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            cl.direct_send(
                text=reply_text,
                thread_ids=[group.id]  # Critical fix here
            )
            logger.info(f"📩 Replied to @{user.username}")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Group error: {str(e)}")
            time.sleep(5)

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting bot")
    
    # Login with retries
    client = None
    for _ in range(3):
        client = login_client()
        if client:
            break
        time.sleep(10)
    
    if not client:
        logger.error("❌ Permanent login failure")
        exit(1)
        
    # Main loop
    while True:
        process_groups(client)
        logger.info("🔄 Next check in 30 seconds...")
        time.sleep(30)
