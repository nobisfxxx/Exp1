import requests
import time
import json

# Your Instagram cookies (make sure you replace it with the cookies you extracted)
COOKIES_JSON = '''[
    {
        "name": "sessionid",
        "value": "4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw",
        "domain": ".instagram.com",
        "secure": true,
        "httpOnly": true,
        "sameSite": "no_restriction",
        "session": false
    },
    {
        "name": "csrftoken",
        "value": "CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf",
        "domain": ".instagram.com",
        "secure": true,
        "httpOnly": false,
        "sameSite": "no_restriction",
        "session": false
    }
]'''

# Convert cookies string to a Python dictionary
cookie_list = json.loads(COOKIES_JSON)
cookies = {cookie['name']: cookie['value'] for cookie in cookie_list}

# Instagram API base URL for sending messages
INSTAGRAM_API_URL = 'https://i.instagram.com/api/v1/'

# Message and Delay
reply_message = "@sender Oii massage maat kar warga nobi aa jaega"
delay_between_replies = 3  # seconds

# Helper function to send reply
def send_reply(message, user_id, group_id):
    url = f"{INSTAGRAM_API_URL}direct_v2/threads/{group_id}/items/"
    data = {
        "user_ids": [user_id],
        "text": message
    }
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 (Windows; U; Windows NT 10.0; en-US; rv:123.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers, cookies=cookies)
    if response.status_code == 200:
        print(f"Message sent to {user_id} in group {group_id}")
    else:
        print(f"Failed to send message to {user_id} in group {group_id}, Status code: {response.status_code}")

# Function to get active group chats (this needs to be implemented correctly for your use)
def get_active_group_chats():
    # You need a method to get the active group chats
    # Example: Return a list of dictionaries with group_id and user_id for each active group
    return [
        {'user_id': '1234567890', 'group_id': 'abcd1234'},
        {'user_id': '0987654321', 'group_id': 'efgh5678'}
    ]

# Main function to reply to all groups
def reply_to_group_chats():
    active_groups = get_active_group_chats()  # Get active groups dynamically

    for group in active_groups:
        user_id = group['user_id']
        group_id = group['group_id']
        message_to_send = reply_message.replace("@sender", user_id)
        send_reply(message_to_send, user_id, group_id)
        time.sleep(delay_between_replies)

# Run the bot
if __name__ == "__main__":
    reply_to_group_chats()
