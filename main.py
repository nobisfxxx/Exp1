import time
import json
import random
from datetime import datetime, timedelta
from instagrapi import Client

# Configuration Constants
DEFAULT_REPLY_MESSAGE = "oii massage maat kar warna lynx ki maa shod ke feekkk dunga"
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work weelll?.. If not make changes the the script.. till then boii boii boss"
STOP_COMMAND = "stop the bot on this gc"
RESUME_COMMAND = "resume the bot on this gc"
PASSWORD_REQUEST = "Okay, boss. What's the password?"
VALID_PASSWORD = "17092004"
REPLY_DELAY = 3  # seconds

# Device and session setup (assuming the cookies are loaded from the file)
def load_session():
    with open('session.json', 'r') as f:
        session_data = json.load(f)
    cl = Client()
    cl.set_device(session_data["device"])
    cl.set_cookie(session_data["cookies"])
    return cl

# Function to check if bot is part of the group
def is_participant(cl, thread_id):
    thread_info = cl.direct_thread(thread_id)
    for participant in thread_info['users']:
        if participant['pk'] == cl.user_id:
            return True
    return False

# Function to send message with custom roast
def send_roast_message(cl, thread_id, message, user_id):
    roast_message = f"{message} @{user_id}"  # Example roast message
    cl.direct_send(roast_message, thread_id)

# Main function to handle message processing
def process_group_messages(cl):
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                thread_id = thread['thread_id']
                last_message = thread['last_activity_at']

                # Skip threads where bot is no longer a participant
                if not is_participant(cl, thread_id):
                    print(f"Skipping {thread_id}, not a participant.")
                    continue

                # Skip if last message is a name change
                if "left the group" in last_message['text']:
                    print(f"Skipping {thread_id}, name change detected.")
                    continue

                # Limit reply to 3 seconds between messages
                print(f"Replying in thread: {thread_id}")
                send_roast_message(cl, thread_id, DEFAULT_REPLY_MESSAGE, thread['users'][0]['username'])
                time.sleep(REPLY_DELAY)  # Respect the delay between messages

        except Exception as e:
            print(f"Error: {str(e)}")
            # Optional: Auto-relogin if session is invalid
            cl = load_session()
            time.sleep(10)

# Main loop to run bot
if __name__ == "__main__":
    client = load_session()
    process_group_messages(client)
