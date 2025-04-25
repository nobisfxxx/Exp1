from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError
import os
import json
import time
import logging
import random

# ===== ENHANCED CONFIGURATION =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration with fallbacks
USERNAME = os.getenv("INSTA_USERNAME", "your_username")
PASSWORD = os.getenv("INSTA_PASSWORD", "your_password")
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Your reply here"

# Latest Instagram settings (July 2024)
LATEST_VERSION = "325.0.0.0.0"
ANDROID_VERSION = 34  # Android 14
ANDROID_RELEASE = "14.0"

# ===== DEVICE CONFIGURATION =====
def get_device_settings():
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

# ===== SESSION MANAGEMENT =====
def create_fresh_session():
    device = get_device_settings()
    session_data = {
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
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

# ===== CHALLENGE HANDLER =====
def handle_challenge(client, challenge_exception):
    logger.warning("🔐 Challenge required - solving...")
    try:
        challenge_info = client.challenge_resolve(challenge_exception)
        if challenge_info.get('action') == 'submit_email':
            # Implement your email code retrieval here
            code = input("Enter email verification code: ")
            client.challenge_code_handler = lambda _: code
        elif challenge_info.get('action') == 'submit_phone':
            # Implement your SMS code retrieval here
            code = input("Enter SMS verification code: ")
            client.challenge_code_handler = lambda _: code
        return client.challenge_resolve(challenge_exception)
    except Exception as e:
        logger.error(f"Challenge failed: {str(e)}")
        return False

# ===== SAFE API HANDLER =====
def safe_api_call(client, func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result is None:
                raise ValueError("API returned None")
            return result
        except ChallengeRequired as e:
            if not handle_challenge(client, e):
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

# ===== ENHANCED LOGIN =====
def initialize_client():
    if not os.path.exists(SESSION_FILE):
        create_fresh_session()
    
    client = Client()
    client.delay_range = [3, 7]  # Human-like delays
    
    try:
        client.load_settings(SESSION_FILE)
        
        # Force new device settings if empty
        if not client.device:
            client.set_device(get_device_settings())
        
        # Login with challenge handling
        try:
            if not client.login(USERNAME, PASSWORD):
                raise Exception("Login returned False")
        except ChallengeRequired as e:
            if not handle_challenge(client, e):
                raise Exception("Challenge failed")
        
        # Verify session is active
        if not safe_api_call(client, client.get_timeline_feed):
            raise Exception("Failed to verify session")
        
        client.dump_settings(SESSION_FILE)
        logger.info("✅ Login successful")
        return client
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        # Create fresh session for next attempt
        create_fresh_session()
        return None

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting enhanced Instagram bot")
    
    # Initialize with retries
    client = None
    for attempt in range(3):
        client = initialize_client()
        if client:
            break
        time.sleep(10)
    
    if not client:
        logger.error("❌ Failed to initialize client after 3 attempts")
        exit(1)
        
    # Main operation loop
    failures = 0
    try:
        while failures < 3:
            try:
                # Process groups with error handling
                groups = safe_api_call(client, client.direct_threads)
                if not groups:
                    logger.warning("No groups found")
                    failures += 1
                    time.sleep(60)
                    continue
                    
                # Your group processing logic here
                # ...
                
                failures = 0  # Reset on success
                cooldown = random.randint(120, 300)
                logger.info(f"⏳ Next check in {cooldown//60}m {cooldown%60}s")
                time.sleep(cooldown)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"Operation error: {str(e)}")
                failures += 1
                time.sleep(300)
        
        if failures >= 3:
            logger.error("🔴 Too many consecutive failures - restart needed")
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
    finally:
        logger.info("🏁 Bot stopped")
