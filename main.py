from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import os
import json
import time
import random

def validate_session_file(session_path):
    """Ensure session.json has correct format"""
    if not os.path.exists(session_path):
        return False
        
    try:
        with open(session_path) as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return False
            if 'cookies' not in data:
                return False
        return True
    except:
        return False

def create_clean_session():
    """Create fresh session file with proper structure"""
    return {
        "cookies": [],
        "last_login": 0,
        "device_settings": {},
        "user_agent": "Instagram 219.0.0.12.117 Android",
        "uuids": {},
        "phone_id": None,
        "device_id": None,
        "adid": None,
        "session_id": None
    }

def login_client():
    cl = Client()
    SESSION_FILE = "session.json"
    
    # 1. Validate or recreate session file
    if not validate_session_file(SESSION_FILE):
        print("Creating fresh session file...")
        with open(SESSION_FILE, 'w') as f:
            json.dump(create_clean_session(), f)
    
    # 2. Configure client
    cl.delay_range = [3, 7]
    cl.set_user_agent("Instagram 219.0.0.12.117 Android")
    
    # 3. Attempt login
    try:
        # First try with session
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)
        
        # Verify login worked
        try:
            cl.get_timeline_feed()
            print("✅ Login successful via session")
            return cl
        except LoginRequired:
            print("⚠ Session expired - trying fresh login")
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
            print("✅ New session created")
            return cl
            
    except ChallengeRequired:
        print("🔐 Challenge required! Check your Instagram app")
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        # Completely reset session if failing
        with open(SESSION_FILE, 'w') as f:
            json.dump(create_clean_session(), f)
    
    return None

if __name__ == "__main__":
    USERNAME = os.getenv("INSTA_USERNAME")
    PASSWORD = os.getenv("INSTA_PASSWORD")
    
    # Try login 3 times with delays
    for attempt in range(3):
        client = login_client()
        if client:
            break
        wait_time = random.randint(30, 120)
        print(f"Retrying in {wait_time} seconds...")
        time.sleep(wait_time)
    else:
        print("Failed after 3 attempts. Check credentials/network.")
        exit(1)
    
    # Main bot logic here
    print("Bot successfully started!")
