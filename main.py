from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "iamnobi")

# Send a reply message
def send_message(recipient_id, username):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={ACCESS_TOKEN}"
    message_text = f"@{username} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"

    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

# Webhook Verification (GET)
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# Handle incoming messages (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    # We'll just use "user" if no name is provided (to avoid API call here)
                    send_message(sender_id, "user")
        return "EVENT_RECEIVED", 200
    else:
        return "Ignored", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default 5000, change with env
    app.run(host="0.0.0.0", port=port)
