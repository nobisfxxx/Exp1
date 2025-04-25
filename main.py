from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "/app/session.json"

def enforce_session_structure():
    """Guarantee valid session structure"""
    if not os.path.exists(SESSION_FILE):
        reset_session_file()
        return

    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict) or 'cookies' not in data:
                raise ValueError("Invalid structure")
    except (json.JSONDecodeError, ValueError):
        logger.warning("Corrupted session file - resetting")
        reset_session_file()

def reset_session_file():
    """Create fresh valid session file"""
    valid_structure = {
        "cookies": [],
        "last_login": int(time.time()),
        "device_settings": {
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2"
        },
        "user_agent": "Instagram 219.0.0.12.117 Android"
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(valid_structure, f, indent=2)
    logger.info("Created new session file")

def login():
    """Robust login with session validation"""
    enforce_session_structure()
    
    cl = Client()
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        
        # Verify session works
        cl.get_timeline_feed()
        logger.info("✅ Login successful")
        return cl
    except (LoginRequired, AttributeError):
        logger.warning("Session expired - fresh login")
        cl = Client()
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        return cl
    except ChallengeRequired:
        logger.error("Complete verification in Instagram app!")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        reset_session_file()
    return None

if __name__ == "__main__":
    logger.info("🚀 Starting container")
    attempt = 0
    while attempt < 3:
        client = login()
        if client:
            logger.info("🤖 Bot operational")
            # Add your group chat logic here
            while True:
                time.sleep(10)
        logger.warning(f"Retrying login ({attempt+1}/3)")
        attempt += 1
        time.sleep(10)
    logger.error("❌ Permanent login failure")
