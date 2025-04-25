from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
import os
import json
import time
import logging
import random

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME") or "your_username"  # Replace or use env
PASSWORD = os.getenv("INSTA_PASSWORD") or "your_password"  # Replace or use env
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# Latest Instagram version as of 2025
LATEST_APP_VERSION = "320.0.0.0.0"
ANDROID_VERSION = 33  # Android 13
ANDROID_RELEASE = "13.0"

# ===== DEVICE SETTINGS =====
def get_current_device():
    return {
        "app_version": LATEST_APP_VERSION,
        "android_version": ANDROID_VERSION,
        "android_release": ANDROID_RELEASE,
        "phone_manufacturer": "OnePlus",
        "phone_device": "ONEPLUS A5010",
        "phone_model": "ONEPLUS 5T",
        "cpu": "qcom",
        "dpi": "380dpi",
        "resolution": "1080x1920",
        "device_id": f"android-{random.randint(10**15, (10**16)-1)}"
    }

# ===== SESSION MANAGEMENT =====
def validate_session():
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            if data.get("device_settings", {}).get("app_version") != LATEST_APP_VERSION:
                logger.warning("Outdated session - resetting device settings")
                return False
        return True
    except Exception:
        return False

def reset_session_file():
    device = get_current_device()
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": device,
            "user_agent": (
                f"Instagram {LATEST_APP_VERSION} Android "
                f"({ANDROID_VERSION}/{ANDROID_RELEASE}; {device['phone_manufacturer']}; "
                f"{device['phone_model']}; {device['cpu']}; en_US; {device['dpi']})"
            )
        }, f)

# ===== GROUP CHAT FUNCTIONS =====
def get_group_chats(cl):
    """Get active group chats with error handling"""
    try:
        threads = cl.direct_threads()
        return [t for t in threads if len(t.users) > 1]  # Filter groups
    except ClientError as e:
        if "Not authorized" in str(e):
            logger.error("❌ Bot was removed from all groups")
        else:
            logger.error(f"Failed to fetch groups: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []

def process_groups(cl):
    """Process messages in groups with safety checks"""
    groups = get_group_chats(cl)
    if not groups:
        logger.warning("No active groups found")
        return False

    for group in groups:
        try:
            logger.info(f"💬 Checking group: {group.id[:4]}...{group.id[-4:]}")
            
            # Get recent messages (max 3 to avoid detection)
            messages = cl.direct_messages(thread_id=group.id, amount=3)
            if not messages:
                continue
                
            last_msg = messages[-1]
            if last_msg.user_id == cl.user_id:
                continue  # Skip own messages
                
            # Send reply with random delay
            user = cl.user_info(last_msg.user_id)
            reply_text = REPLY_TEMPLATE.format(username=user.username)
            
            time.sleep(random.uniform(3.0, 8.0))  # Human-like delay
            cl.direct_send(text=reply_text, thread_ids=[group.id])
            logger.info(f"📩 Replied to @{user.username}")
            
        except ClientError as e:
            if "Not in group" in str(e):
                logger.error(f"🚫 Removed from group {group.id[:4]}...")
                continue
            logger.error(f"Group error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        
        time.sleep(random.randint(5, 15))  # Delay between groups
    
    return True  # Still active in groups

# ===== LOGIN HANDLER =====
def login_client():
    if not validate_session():
        reset_session_file()
    
    cl = Client()
    cl.delay_range = [2, 5]  # Human-like delays
    
    try:
        cl.load_settings(SESSION_FILE)
        time.sleep(random.uniform(1.0, 3.0))
        
        if not cl.device:
            cl.set_device(get_current_device())
            
        if cl.login(USERNAME, PASSWORD):
            cl.get_timeline_feed()  # Verify API access
            cl.dump_settings(SESSION_FILE)
            logger.info("✅ Login successful")
            return cl
            
    except ChallengeRequired:
        logger.error("🔐 Verification required - check your phone")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        reset_session_file()
    
    return None

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting enhanced Instagram bot")
    
    # Login with retries
    client = None
    for attempt in range(3):
        delay = 2 ** attempt + random.random()
        logger.info(f"Attempt {attempt+1}/3 - Waiting {delay:.1f}s")
        time.sleep(delay)
        
        client = login_client()
        if client:
            break
    
    if not client:
        logger.error("❌ Failed to login after 3 attempts")
        exit(1)
        
    # Main loop
    try:
        while True:
            if not process_groups(client):
                logger.warning("No groups active - stopping")
                break
                
            delay = random.randint(120, 300)  # 2-5 minutes
            logger.info(f"⏳ Next check in {delay//60}m {delay%60}s")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
    except Exception as e:
        logger.error(f"CRASH: {str(e)}")
