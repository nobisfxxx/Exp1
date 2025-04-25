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

# Configuration
USERNAME = os.getenv("INSTA_USERNAME") or "your_username"
PASSWORD = os.getenv("INSTA_PASSWORD") or "your_password"
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Your message here"

# ===== ENHANCED SESSION HANDLER =====
def create_fresh_session():
    device = {
        "app_version": "320.0.0.0.0",
        "android_version": 33,
        "android_release": "13.0",
        "phone_manufacturer": "OnePlus",
        "phone_device": "ONEPLUS A5010",
        "phone_model": "ONEPLUS 5T",
        "device_id": f"android-{random.randint(10**15, (10**16)-1)}"
    }
    
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": device,
            "user_agent": (
                f"Instagram 320.0.0.0.0 Android (33/13.0; OnePlus; ONEPLUS 5T; "
                f"qcom; en_US; 380dpi)"
            )
        }, f)

# ===== SMART API REQUEST HANDLER =====
def safe_api_call(cl, func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result is None:
                raise ValueError("API returned None")
            return result
        except Exception as e:
            wait = min(2 ** attempt + random.random(), 15)  # Max 15s wait
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {str(e)} - Waiting {wait:.1f}s")
            time.sleep(wait)
    
    logger.error(f"Permanent failure calling {func.__name__}")
    return None

# ===== GROUP CHAT PROCESSOR =====
def process_groups(cl):
    try:
        # Get groups with error handling
        threads = safe_api_call(cl, cl.direct_threads)
        if not threads:
            return False

        groups = [t for t in threads if len(t.users) > 1]
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
                messages = safe_api_call(cl, cl.direct_messages, thread_id=group.id, amount=3)
                if not messages:
                    continue

                # Process last message
                last_msg = messages[-1]
                if last_msg.user_id == cl.user_id:
                    continue

                # Send reply
                user = safe_api_call(cl, cl.user_info, last_msg.user_id)
                if not user:
                    continue

                reply_text = REPLY_TEMPLATE.format(username=user.username)
                time.sleep(random.uniform(5.0, 10.0))
                
                if safe_api_call(cl, cl.direct_send, text=reply_text, thread_ids=[group.id]):
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
    logger.info("🚀 Starting Instagram bot")
    
    # Initialize fresh session if needed
    if not os.path.exists(SESSION_FILE):
        create_fresh_session()

    # Login with resilience
    cl = Client()
    cl.delay_range = [3, 7]
    
    try:
        cl.load_settings(SESSION_FILE)
        if not cl.login(USERNAME, PASSWORD):
            raise Exception("Login failed")
        
        cl.dump_settings(SESSION_FILE)
        logger.info("✅ Login successful")
        
        # Main loop with cooldown periods
        failures = 0
        while failures < 3:
            try:
                if not process_groups(cl):
                    failures += 1
                    logger.warning(f"Temporary failure ({failures}/3)")
                else:
                    failures = 0
                
                # Random cooldown (3-8 minutes)
                cooldown = random.randint(180, 480)
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
            logger.error("🔴 Too many failures - restart recommended")
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
