import json
import random
from instagrapi import Client
from datetime import datetime, timedelta

# Load session cookies from session_cookies.json
with open('session_cookies.json', 'r') as file:
    cookies = json.load(file)

# Initialize the Instagram client
cl = Client()

# Set the cookies for the session login
cl.set_cookies(cookies)

# Custom roast messages
ROAST_MESSAGES = [
    "I would agree with you, but then we’d both be wrong.",
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "You're proof that even Google doesn't have all the answers.",
    "I’d explain it to you, but I left my English-to-Dingbat dictionary at home.",
    "If I had a dollar for every time you said something intelligent, I'd be broke."
]

# Time to skip old messages (in seconds)
TIME_THRESHOLD = 60  # Only reply to messages within the last 60 seconds

# Helper function to check if the message is recent
def is_recent_message(timestamp):
    message_time = datetime.fromtimestamp(timestamp)
    return datetime.now() - message_time <= timedelta(seconds=TIME_THRESHOLD)

# Function to send a roast message to a group
def send_roast_reply(group_id, sender_username):
    try:
        roast_message = random.choice(ROAST_MESSAGES)  # Pick a random roast
        message = f"@{sender_username}, {roast_message}"
        cl.direct_send(message, [group_id])
        print(f"Roast sent to @{sender_username}: {message}")
    except Exception as e:
        print(f"Error sending roast message: {e}")

# Function to get recent messages from a group
def check_and_reply_to_messages():
    try:
        # Fetch the threads in your inbox (group chats)
        threads = cl.direct_threads()
        
        for thread in threads:
            # Skip threads where you're not a participant
            if not cl.user_info(thread.user_id).is_private:
                continue
            
            for message in thread.messages:
                # Check if the message is within the time threshold
                if is_recent_message(message.timestamp):
                    # Only reply to messages that are recent
                    sender_username = message.user.username
                    send_roast_reply(thread.id, sender_username)
    except Exception as e:
        print(f"Error checking messages: {e}")

# Main bot loop to keep checking messages every few seconds
while True:
    check_and_reply_to_messages()
