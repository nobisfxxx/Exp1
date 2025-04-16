import requests
import json
import time

# Define your cookies and API URL
cookies = {
    "sessionid": "4815764655%3AKIze6plmPWbhIc%3A5%3AAYeKoHWOIAtE_3qGgiW1mHJ1qXJBVTma2g5HbUr3Cw",
    "ds_user_id": "4815764655",
    "csrftoken": "CnUT88Fi2a1yAzOp1ACYqMKj6gRfs6Lf",
    "ig_did": "01ECD94D-82CA-4A2B-B39C-21F48E6309E0",
    "mid": "Z_-yPwABAAGrQkPVuZUxYwTPbtND",
    "rur": "\"PRN\\0544815764655\\0541776346914:01f70c1c6b15d54b0fa9377fa5465397bb70f7045f7415af439dbb8586e431fced2c06fb\"",
    # Add all other relevant cookies
}

INSTAGRAM_API_URL = "https://i.instagram.com/api/v1/direct_v2/threads/"

# Define message format
def send_reply(message, user_id, group_id):
    url = f"{INSTAGRAM_API_URL}{group_id}/items/"
    data = {
        "user_ids": [user_id],
        "text": message
    }
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 (Windows; U; Windows NT 10.0; en-US; rv:123.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Content-Type": "application/json"
    }

    try:
        # Make the request to send the message
        response = requests.post(url, json=data, headers=headers, cookies=cookies)
        
        # Check the status code
        if response.status_code == 200:
            print(f"Message sent to {user_id} in group {group_id}")
        else:
            print(f"Failed to send message to {user_id} in group {group_id}, Status code: {response.status_code}")
            print("Response content:", response.text)  # Print response body for more details
            
    except Exception as e:
        print(f"Error occurred while sending message to {user_id} in group {group_id}: {str(e)}")

# Function to check if the bot has been kicked out
def check_if_kicked(group_id):
    url = f"{INSTAGRAM_API_URL}{group_id}/info/"
    response = requests.get(url, cookies=cookies)
    
    if response.status_code == 200:
        group_info = response.json()
        if 'participants' in group_info:
            participants = group_info['participants']
            if 'user_id' in participants and participants['user_id'] != cookies['ds_user_id']:
                return True
    return False

# Function to reply to all group chats with a delay
def reply_to_all_groups():
    group_ids = ["abcd1234", "efgh5678"]  # Example group IDs
    user_ids = ["1234567890", "0987654321"]  # Example user IDs
    reply_message = "@sender Oii massage maat kar warga nobi aa jaega"
    
    for group_id in group_ids:
        # Check if bot has been kicked
        if check_if_kicked(group_id):
            print(f"Bot has been kicked from group {group_id}, skipping...")
            continue
        
        for user_id in user_ids:
            send_reply(reply_message, user_id, group_id)
            time.sleep(3)  # Delay between replies

if __name__ == "__main__":
    reply_to_all_groups()
