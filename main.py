from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import os
import random
from datetime import datetime

# Configuration
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
SESSION_FILE = "session.json"
REPLY_MSG = "@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
MIN_DELAY = 5  # seconds
MAX_DELAY = 15  # seconds
PROXY = None  # "http://user:pass@ip:port"

def create_client():
    cl = Client()
    cl.delay_range = [MIN_DELAY, MAX_DELAY]
    
    if PROXY:
        cl.set_proxy(PROXY)
    
    # Set realistic device/user-agent
    cl.set_user_agent("Instagram 219.0.0.12.117 Android")
    cl.set_device({
        "app_version": "219.0.0.12.117",
        "android_version": 25,
        "android_release": "7.1.2"
    })
    return cl

def login_helper(cl):
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
        
        login_via_session = False
        login_via_pw = False

        if cl.settings:
            try:
                cl.get_timeline_feed()
                login_via_session = True
            except LoginRequired:
                print("Session expired - logging in with password")
                cl.login(USERNAME, PASSWORD)
                login_via_pw = True
        else:
            print("No session found - logging in with password")
            cl.login(USERNAME, PASSWORD)
            login_via_pw = True

        if login_via_pw:
            cl.dump_settings(SESSION_FILE)
            print("New session saved")
        
        return True
    except ChallengeRequired:
        print("Challenge required! Check your Instagram app")
        return False
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

def safe_reply(cl, thread):
    try:
        last_msg = thread.messages[-1]
        user_id = last_msg.user_id
        user_info = cl.user_info(user_id)
        
        if user_info.username.lower() != USERNAME.lower():  # Don't reply to self
            reply_text = REPLY_MSG.format(username=user_info.username)
            cl.direct_send(reply_text, thread_id=thread.id)
            print(f"{datetime.now()} - Replied to @{user_info.username}")
            
            # Random delay between actions
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)
    except Exception as e:
        print(f"Error in reply: {str(e)}")
        time.sleep(60)

def main():
    cl = create_client()
    
    if not login_helper(cl):
        print("Failed to login. Exiting.")
        return

    print("Bot started - Ctrl+C to stop")
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                if len(thread.users) > 1:  # Only group chats
                    safe_reply(cl, thread)
            
            # Random pause between checks
            time.sleep(random.randint(30, 120))
        except KeyboardInterrupt:
            print("Stopping bot...")
            break
        except Exception as e:
            print(f"Main error: {str(e)}")
            time.sleep(300)  # Wait 5 minutes on major errors

if __name__ == "__main__":
    main()
