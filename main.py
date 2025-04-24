import time
import requests
from flask import Flask, jsonify

# Replace with your Instagram long-term access token
ACCESS_TOKEN = 'IGAAYMtqnh68pBZAFAxSlNkbHlCVnNxMTR2eWxNbVBMd2RUVC1jaWNPMmVlTW95WER1MkUtRDRudUxuMUxwcFJXRnVIblVxYjVYMzRfWVhFNk44N3hpdVp5cHVlMkpYdmc2aEJBLXg1SVo5dy1HWlRZAa0ZALSHZAFZAUMta3RuNUdyYwZDZD'

# Instagram Graph API URL
GRAPH_API_URL = 'https://graph.instagram.com'

# Reply message template
REPLY_MESSAGE = "@sender Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

# Set up Flask app
app = Flask(__name__)

# Function to get user details using the long-term access token
def get_user_details():
    url = f"{GRAPH_API_URL}/me?fields=id,username&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    return response.json()

# Function to get messages from the group chat
def get_group_messages():
    url = f"{GRAPH_API_URL}/me/conversations?access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    return response.json()

# Function to send a reply message to a group chat
def send_reply_to_group_chat(group_id, message):
    url = f"{GRAPH_API_URL}/{group_id}/messages"
    data = {
        'message': message,
        'access_token': ACCESS_TOKEN
    }
    response = requests.post(url, data=data)
    return response.json()

# Function to check if the bot is kicked from a group chat
def check_if_kicked(group_id):
    url = f"{GRAPH_API_URL}/{group_id}/participants?access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    participants = response.json().get('data', [])
    # Check if the bot is part of the group
    for participant in participants:
        if participant['id'] == get_user_details()['id']:
            return True
    return False

# Route to send replies to all group chats
@app.route('/send_replies', methods=['GET'])
def send_replies():
    groups = get_group_messages()
    for group in groups.get('data', []):
        group_id = group['id']
        
        # Check if the bot is kicked from the group
        if check_if_kicked(group_id):
            continue  # Skip this group if bot is kicked
        
        # Send reply to the group
        message = REPLY_MESSAGE.replace("@sender", group['name'])  # Customize the reply
        send_reply_to_group_chat(group_id, message)
        
        # Wait for 3 seconds before sending the next reply
        time.sleep(3)
    
    return jsonify({"status": "Replied to all group chats."})

@app.route('/')
def home():
    return "Instagram Bot is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
