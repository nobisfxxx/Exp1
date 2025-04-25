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

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"  # Updated path
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# Latest Instagram version as of 2025
LATEST_APP_VERSION = "320.0.0.0.0"
ANDROID_VERSION = 33  # Android 13
ANDROID_RELEASE = "13.0"

# ===== UPDATED DEVICE SETTINGS =====
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
        "device_id": f"android-{random.randint(100000000000000, 999999999999999)}"
    }

# ===== ENHANCED SESSION MANAGEMENT =====
def validate_session():
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            # Force update device settings if outdated
            if data.get("device_settings", {}).get("app_version") != LATEST_APP_VERSION:
                logger.warning("Outdated session - resetting device settings")
                return False
        return True
    except Exception:
        return False

def reset_session_file():
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            "cookies": [],
            "last_login": int(time.time()),
            "device_settings": get_current_device(),
            "user_agent": (
                f"Instagram {LATEST_APP_VERSION} Android "
                f"({ANDROID_VERSION}/{ANDROID_RELEASE}; {get_current_device()['phone_manufacturer']}; "
                f"{get_current_device()['phone_model']}; {get_current_device()['cpu']}; "
                f"en_US; {get_current_device()['dpi']})"
            )
        }, f)

# ===== ROBUST LOGIN HANDLER =====
def login_client():
    if not validate_session():
        reset_session_file()
    
    cl = Client()
    cl.delay_range = [3, 7]  # More human-like delays
    
    try:
        # Load with updated settings
        cl.load_settings(SESSION_FILE)
        
        # Pre-login check
        time.sleep(random.uniform(2.0, 5.0))
        
        # Force new device ID if needed
        if not cl.device:
            cl.set_device(get_current_device())
            
        login_result = cl.login(USERNAME, PASSWORD)
        
        # Post-login verification
        if login_result:
            cl.get_timeline_feed()  # Test API access
            cl.dump_settings(SESSION_FILE)
            logger.info("✅ Login successful with new session")
            return cl
            
    except ChallengeRequired:
        logger.error("🔐 Challenge required - verify login manually")
        # You can implement challenge resolution here
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        # Rotate device ID on failure
        reset_session_file()
    
    return None

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    logger.info("🚀 Starting bot with enhanced anti-detection")
    
    # Login with exponential backoff
    max_retries = 3
    client = None
    
    for attempt in range(max_retries):
        wait_time = 2 ** attempt + random.random()
        logger.info(f"Attempt {attempt + 1}/{max_retries} - Waiting {wait_time:.1f}s")
        time.sleep(wait_time)
        
        client = login_client()
        if client:
            break
            
    if not client:
        logger.error("❌ Permanent login failure - check credentials or wait 24h")
        exit(1)
        
    # Main loop with safety checks
    try:
        while True:
            if not process_groups(client):  # Reuse your existing function
                logger.warning("No active groups - stopping")
                break
                
            # Random delay between 1-5 minutes
            delay = random.randint(60, 300)
            logger.info(f"🔄 Next check in {delay//60}m {delay%60}s")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
