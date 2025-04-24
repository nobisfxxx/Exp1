from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Environment variables
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == "POST":
        # Process incoming messages
        data = request.get_json()
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message = messaging_event["message"]["text"]
                    # Craft your custom reply here
                    reply = f"@{sender_id} Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
                    send_message(sender_id, reply)
        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message):
    # Send the response to the user via Facebook Messenger API
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

if __name__ == "__main__":
    # Ensure it's running on the right port (5000 or 8080 depending on the environment)
    app.run(host="0.0.0.0", port=5000)
