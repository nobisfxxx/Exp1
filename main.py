from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import random
from datetime import datetime

# ===== CONFIGURATION =====
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"
REPLY_TEMPLATE = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# ===== SESSION VALIDATOR =====
def validate_session_structure(session_data):
    required_keys = ['cookies', 'last_login', 'device_settings', 'user_agent']
    return all(key in session_data for key in required_keys)

def fix_session_file():
    """Create properly structured session file"""
    valid_structure = {
        "cookies": [],
        "last_login": 0,
        "device_settings": {
            "app_version": "219.0.0.12.117",
            "android_version": 25,
            "android_release": "7.1.2",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "ONEPLUS A6013"
        },
        "user_agent": "Instagram 219.0.0.12.117 Android"
    }
    with open(SESSION_FILE, 'w') as f:
        json.dump(valid_structure, f)

# ===== AUTHENTICATION =====
def login_client():
    cl = Client()
    
    # 1. Validate/Create session file
    if not os.path.exists(SESSION_FILE):
        fix_session_file()
    else:
        try:
            with open(SESSION_FILE) as f:
                data = json.load(f)
                if not validate_session_structure(data):
                    print("⚠ Invalid session structure - resetting")
                    fix_session_file()
        except json.JSONDecodeError:
            print("⚠ Corrupted session file - resetting")
            fix_session_file()

    # 2. Attempt login
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        
        # Verify session
        cl.get_timeline_feed()
        print("✅ Login successful!")
        return cl
        
    except (LoginRequired, AttributeError) as e:
        print(f"⚠ Session expired: {str(e)} - Trying fresh login")
        cl = Client()
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        return cl
        
    except ChallengeRequired:
        print("🔐 Complete verification in Instagram app!")
        return None

# ===== MAIN =====
if __name__ == "__main__":
    # Attempt login 3 times
    for _ in range(3):
        client = login_client()
        if client:
            print("🤖 Bot started successfully!")
            # Add your group reply logic here
            break
        time.sleep(30)
    else:
        print("❌ Permanent login failure")
