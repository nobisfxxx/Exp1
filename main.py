import json
import time
import requests

# Load cookies from a JSON file
with open("cookies.json", "r") as f:
    cookies = json.load(f)

# Define your custom reply message
def custom_reply_message(sender):
    return f"@{sender} Oii massage maat kar warga nobi aa jaega"

# Instagram API base URL
BASE_URL = "https://i.instagram.com/api/v1"

# Headers for making requests with cookies
headers = {
    "User-Agent": "Instagram 272.0.0.18.84 Android (Android 14, Infinix GT 10 Pro)",
    "Accept-Language": "en-US",
    "Connection": "close",
}

# Function to create a session with the provided cookies
def create_session():
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"])
    return session

# Function to check if the bot has been kicked out of a group chat
def is_kicked_from_group(session, group_id):
    try:
        response = session.get(f"{BASE_URL}/groups/{group_id}/info/")
        if response.status_code == 200:
            group_data = response.json()
            # Check if the bot is still part of the group
            for member in group_data['members']:
                if member['username'] == 'your_instagram_username':
                    return False  # Not kicked
            return True  # Kicked
        else:
            print(f"Failed to check group {group_id}: {response.text}")
            return False
    except Exception as e:
        print(f"Error checking kicked status for group {group_id}: {e}")
        return False

# Function to send the custom reply message to the group
def send_reply(session, group_id, message):
    try:
        payload = {
            "message": message,
            "group_id": group_id
        }
        response = session.post(f"{BASE_URL}/groups/{group_id}/send_message/", data=payload, headers=headers)
        if response.status_code == 200:
            print(f"Message sent to group {group_id}: {message}")
        else:
            print(f"Failed to send message to group {group_id}: {response.text}")
    except Exception as e:
        print(f"Error sending message to group {group_id}: {e}")

# Main function to process the group chats
def process_groups():
    session = create_session()  # Create a session with the cookies

    while True:
        # Replace with actual group IDs and usernames
        group_ids = ["group1_id", "group2_id", "group3_id"]  # Example group IDs
        for group_id in group_ids:
            if not is_kicked_from_group(session, group_id):
                sender = "example_sender"  # Replace with actual sender logic
                message = custom_reply_message(sender)
                send_reply(session, group_id, message)
            else:
                print(f"Bot is kicked from group {group_id}. Skipping...")
        
        time.sleep(3)  # Delay between replies to stay under radar

if __name__ == "__main__":
    process_groups()
