from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Your Facebook Page Access Token and Verify Token
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        # Verify the token sent by Facebook
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Verification successful.")
            return challenge, 200
        else:
            print("Verification token mismatch.")
            return "Verification token mismatch", 403

    elif request.method == "POST":
        # Facebook sends the message data here
        data = request.get_json()
        print("Received data:", data)  # Log incoming data
        
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message = messaging_event["message"].get("text", "")
                    print(f"Message from {sender_id}: {message}")
                    
                    # Only reply if the message is from a group (you can filter here)
                    if "text" in messaging_event["message"]:
                        reply = f"@{sender_id} Oii message maat kar, warga nobi aa jaega 😡🪓🌶"
                        send_message(sender_id, reply)
        return "EVENT_RECEIVED", 200


def send_message(recipient_id, message):
    """Send a message to the sender."""
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    
    # Make the request to send a message
    response = requests.post(url, json=payload, headers=headers)
    
    # Log the response from Facebook's API
    if response.status_code == 200:
        print(f"Successfully sent message to {recipient_id}")
    else:
        print(f"Failed to send message. Error: {response.text}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
