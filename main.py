from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
import os
import json
import time
import logging
import random
from datetime import datetime

# ===== CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME") or "your_username"
PASSWORD = os.getenv("INSTA_PASSWORD") or "your_password"
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Your reply here"

# Updated as of July 2024
LATEST_VERSION = "325.0.0.0.0"
ANDROID_VERSION = 34  # Android 14
ANDROID_RELEASE = "14.0"

# ===== ENHANCED SESSION MANAGEMENT =====
def create_device_settings():
    return {
        "app_version": LATEST_VERSION,
        "android_version": ANDROID_VERSION,
        "android_release": ANDROID_RELEASE,
        "phone_manufacturer": "OnePlus",
        "phone_device": "ONEPLUS A6013",
        "phone_model": "ONEPLUS 6T",
        "cpu": "qcom",
        "dpi": "420dpi",
        "resolution": "1080x2280",
        "device_id": f"android-{random.randint(10**15, 10**16-1)}"
    }

def create_fresh_session():
    device = create_device_settings()
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": device,
            "user_agent": (
                f"Instagram {LATEST_VERSION} Android "
                f"({ANDROID_VERSION}/{ANDROID_RELEASE}; "
                f"{device['phone_manufacturer']}; "
                f"{device['phone_model']}; {device['cpu']}; "
                f"en_US; {device['dpi']})"
            )
        }, f)

# ===== CHALLENGE HANDLER =====
def handle_challenge(cl, challenge_exception):
    logger.warning("🔐 Challenge required - solving...")
    try:
        challenge_info = cl.challenge_resolve(challenge_exception)
        if challenge_info.get('action') == 'submit_email':
            # Replace with your email if needed
            cl.challenge_code_handler = lambda _: input("Enter email code: ")
        elif challenge_info.get('action') == 'submit_phone':
            cl.challenge_code_handler = lambda _: input("Enter SMS code: ")
        cl.challenge_resolve(challenge_exception)
        return True
    except Exception as e:
        logger.error(f"Failed to solve challenge: {str(e)}")
        return False

# ===== SAFE API WRAPPER =====
def safe_api_call(cl, func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result is None:
                raise ValueError("API returned None")
            return result
        except ChallengeRequired as e:
            if not handle_challenge(cl, e):
                raise
        except (ClientError, AttributeError) as e:
            wait = min(2 ** attempt + random.random(), 15)
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
            time.sleep(wait)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    logger.error(f"Permanent failure calling {func.__name__}")
    return None

# ===== GROUP CHAT HANDLER =====
def process_groups(cl):
    try:
        # Get groups safely
        threads = safe_api_call(cl, cl.direct_threads)
        if not threads:
            logger.warning("No threads returned")
            return False

        groups = [t for t in threads if hasattr(t, 'users') and len(t.users) > 1]
        if not groups:
            logger.info("No active groups found")
            return False

        for group in groups:
            try:
                # Verify group access
                group_info = safe_api_call(cl, cl.direct_thread, group.id)
                if not group_info:
                    logger.warning(f"Lost access to group {group.id[:4]}...")
                    continue

                # Get messages safely
                messages = safe_api_call(cl, cl.direct_messages, 
                                      thread_id=group.id, amount=3)
                if not messages:
                    continue

                # Process last message
                last_msg = messages[-1]
                if not hasattr(last_msg, 'user_id') or last_msg.user_id == cl.user_id:
                    continue

                # Get user safely
                user = safe_api_call(cl, cl.user_info, last_msg.user_id)
                if not user:
                    continue

                # Send reply with delay
                reply_text = REPLY_TEMPLATE.format(username=user.username)
                time.sleep(random.uniform(5.0, 10.0))
                
                if safe_api_call(cl, cl.direct_send, 
                               text=reply_text, thread_ids=[group.id]):
                    logger.info(f"Replied to @{user.username}")
                else:
                    logger.warning("Failed to send reply")
                
            except Exception as e:
                logger.error(f"Group error: {str(e)}")
            
            time.sleep(random.randint(10, 20))
        
        return True
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        return False

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting enhanced Instagram bot")
    
    # Initialize fresh session if needed
    if not os.path.exists(SESSION_FILE):
        create_fresh_session()

    # Login with resilience
    cl = Client()
    cl.delay_range = [3, 7]  # Human-like delays
    
    try:
        cl.load_settings(SESSION_FILE)
        
        # Force new device if needed
        if not cl.device:
            cl.set_device(create_device_settings())
        
        # Login with challenge handling
        try:
            if not cl.login(USERNAME, PASSWORD):
                raise Exception("Login returned False")
        except ChallengeRequired as e:
            if not handle_challenge(cl, e):
                raise Exception("Challenge failed")
        
        # Verify session
        if not safe_api_call(cl, cl.get_timeline_feed):
            raise Exception("Failed to verify session")
        
        cl.dump_settings(SESSION_FILE)
        logger.info("✅ Login successful")
        
        # Main loop with cooldown
        failures = 0
        while failures < 3:
            try:
                if not process_groups(cl):
                    failures += 1
                    logger.warning(f"Temporary failure ({failures}/3)")
                else:
                    failures = 0
                
                # Random cooldown (2-5 minutes)
                cooldown = random.randint(120, 300)
                logger.info(f"⏳ Next check in {cooldown//60}m {cooldown%60}s")
                time.sleep(cooldown)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"Loop error: {str(e)}")
                failures += 1
                time.sleep(300)  # 5min wait on critical errors
        
        if failures >= 3:
            logger.error("🔴 Too many failures - restart needed")
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
    finally:
        logger.info("🏁 Bot stopped")
