import time
import random
from cy_device_spoofing import random_roast  # Importing the Cython function for roasts
from instagrapi import Client
import json

# Constants and Settings
TRIGGER_PHRASE = "hoi nobi is here"
TRIGGER_RESPONSE = "hey boss.. I missed you... Am I doing my work weelll?.. If not make changes the the script.. till then boii boii boss"
STOP_COMMAND = "stop the bot on this gc"
RESUME_COMMAND = "resume the bot on this gc"
PASSWORD_REQUEST = "Okay, boss. What's the password?"
VALID_PASSWORD = "17092004"

# Initialize the Instagram Client
cl = Client()

# Function to load session cookies
def load_session():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    cl.set_cookies(cookies)

# Login with cookies
def login():
    load_session()
    cl.login_by_cookie()

# Function to handle message replies
def reply_to_group(thread_id, message_id, response):
    cl.direct_send(text=response, thread_id=thread_id)

# Function to check if the message contains a trigger phrase
def check_for_trigger(text):
    if TRIGGER_PHRASE in text:
        return True
    return False

# Function to reply with a roast
def reply_with_roast(sender, thread_id):
    roast = f"@{sender} " + random_roast()  # Getting a random roast from Cython
    reply_to_group(thread_id, sender, roast)

# Main bot loop for responding to messages
def bot_loop():
    # Logging in
    login()

    last_reply_time = {}
    while True:
        threads = cl.direct_threads()  # Get all active threads (group chats)
        
        for thread in threads:
            if not thread.messages:
                continue  # Skip if no messages

            last_msg = thread.messages[0]
            sender = last_msg.user.username
            text = last_msg.text

            # If the message contains the trigger phrase, send a response
            if check_for_trigger(text):
                reply_to_group(thread.thread_id, last_msg.id, TRIGGER_RESPONSE)
            else:
                # Check if the last reply time is less than 3 seconds to avoid spam
                if time.time() - last_reply_time.get(thread.thread_id, 0) < 3:
                    continue

                # Send a roast response
                reply_with_roast(sender, thread.thread_id)
                last_reply_time[thread.thread_id] = time.time()

            time.sleep(1)  # Sleep for 1 second to avoid overwhelming the server

if __name__ == "__main__":
    try:
        bot_loop()  # Run the bot loop
    except Exception as e:
        print(f"Error occurred: {e}")
