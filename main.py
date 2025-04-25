import requests
import time
import json
from flask import Flask, request

# Replace this with your long-lived Page Access Token
ACCESS_TOKEN = "EAARRZBUyQvwYBO7xhHidlxI9dP5VogC2JPhxKeZALp38oKnwpNe6meLHmMMQdZCQSZAhnX9hcLYZAeu1N3RJtEeZAIw5z9uHAjqOfAsDeYLbs2mEGeBeRhEowN5ZAhIhY2iER2I4mPHKlrzmUS8jahW1ZA76s914m8AiH4N1umWZCixCig8nVAnW1"

# Instagram Page ID (not user ID)
PAGE_ID = "556597670881223"

# App secret (if you want to verify signature headers)
VERIFY_TOKEN = "iamnobi"

# Message reply content
AUTO_REPLY_TEXT = "Hey there! massage kiyaaa toh tere maa shod dunga."

# Start Flask app to listen to Webhooks
app = Flask(__name__)

# Logging incoming messages
def log_conversation(entry_id, sender_id, message_text):
    with open("messages_log.json", "a") as f:
        f.write(json.dumps({
            "entry_id": entry_id,
            "sender_id": sender_id,
            "message": message_text,
            "timestamp": time.time()
        }) + "\n")

# Send reply using the Instagram Graph API
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE"
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Sent reply to {recipient_id}: {text}")
    return response.json()

# Webhook verification endpoint
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified")
        return challenge
    else:
        return "Verification failed", 403

# Receive messages from Instagram
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging_events = entry.get("messaging", [])
            for event in messaging_events:
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {}).get("text")
                if sender_id and message:
                    log_conversation(entry["id"], sender_id, message)
                    send_message(sender_id, AUTO_REPLY_TEXT)
    return "OK", 200

# Start local Flask server
if __name__ == "__main__":
    print("Bot is running. Listening for messages...")
    app.run(host="0.0.0.0", port=5000)
