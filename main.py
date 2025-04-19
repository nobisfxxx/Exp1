import os
import time
import json
from instapy import InstaPy  # Assuming InstaPy or similar library is used for automation

# Retrieve session cookies from environment variables (set up in Railway or in a .env file)
session_id = os.getenv("SESSION_ID")
ds_user_id = os.getenv("DS_USER_ID")
csrftoken = os.getenv("CSRFTOKEN")
mid = os.getenv("MID")
ig_did = os.getenv("IG_DID")

# Function to check if the bot is logged in
def is_logged_in(session):
    try:
        session.browser.get("https://www.instagram.com")
        if session.browser.current_url == "https://www.instagram.com/accounts/login/":
            return False
        return True
    except Exception as e:
        print(f"Error during login check: {e}")
        return False

# Function to log in using cookies
def login_with_cookies(session):
    cookies = [
        {"name": "sessionid", "value": session_id, "domain": ".instagram.com", "secure": True, "httpOnly": True},
        {"name": "ds_user_id", "value": ds_user_id, "domain": ".instagram.com", "secure": True, "httpOnly": False},
        {"name": "csrftoken", "value": csrftoken, "domain": ".instagram.com", "secure": True, "httpOnly": False},
        {"name": "mid", "value": mid, "domain": ".instagram.com", "secure": True, "httpOnly": False},
        {"name": "ig_did", "value": ig_did, "domain": ".instagram.com", "secure": True, "httpOnly": True},
    ]
    session.set_sess_cookies(cookies)

# Initialize InstaPy session
session = InstaPy(username=None, password=None, headless_browser=True)

# Log in with cookies
login_with_cookies(session)

# Check if logged in
if not is_logged_in(session):
    print("Login failed, please check cookies.")
    exit()

# Function to handle replying to the latest message in a group chat
def reply_to_latest_message(session):
    try:
        # Get the latest messages from Instagram DMs
        messages = session.grab_latest_direct_messages()

        if not messages:
            print("No messages to reply to.")
            return
        
        latest_message = messages[0]  # Assuming the first message is the latest
        sender = latest_message['sender']
        message_content = latest_message['text']

        # Check if the message is recent (e.g., within the last 60 seconds)
        if time.time() - latest_message['timestamp'] < 60:
            # Craft a roast reply (for example purposes)
            reply_message = f"Hey {sender}, you really thought this message would impress me? 😂"
            print(f"Replying to {sender}: {reply_message}")
            
            # Send the reply
            session.send_message(reply_message, user_id=sender)
        else:
            print("No recent messages to reply to.")
    except Exception as e:
        print(f"Error while replying: {e}")

# Main loop to keep the bot running
while True:
    reply_to_latest_message(session)
    time.sleep(3)  # Adjust the sleep time to limit how often the bot checks for new messages
