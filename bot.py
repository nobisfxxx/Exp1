import json
import time
import random
from instagrapi import Client
from roast_messages import get_random_roast

# Load cookies from cookies.json file
def load_cookies():
    with open("cookies.json", "r") as file:
        return json.load(file)

# Initialize Instagram client and log in using cookies
def login_with_cookies():
    cl = Client()
    cookies = load_cookies()
    cl.set_cookies(cookies)
    return cl

# Function to reply to group messages
def reply_to_group(cl, group_id, message):
    try:
        cl.direct_send(message, [group_id])
        print(f"Replied to group {group_id} with message: {message}")
    except Exception as e:
        print(f"Error replying to group {group_id}: {str(e)}")

# Main loop for the bot to check for messages
def main():
    cl = login_with_cookies()
    while True:
        messages = cl.direct_threads()
        for thread in messages:
            # Only reply to active messages in groups
            if thread.last_activity_at:
                message = get_random_roast(thread.users[0].username)
                reply_to_group(cl, thread.id, message)
        time.sleep(3)  # Delay between checks

if __name__ == "__main__":
    main()
