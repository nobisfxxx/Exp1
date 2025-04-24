from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram Bot is alive!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token mismatch", 403

    elif request.method == "POST":
        data = request.get_json()
        if data:
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    sender_id = event["sender"]["id"]
                    recipient_id = event["recipient"]["id"]
                    
                    if "message" in event and "text" in event["message"]:
                        message_text = event["message"]["text"]
                        # Here: Add group ID check logic if needed
                        reply_text = "Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
                        send_message(sender_id, reply_text)
        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Sent to {recipient_id}: {message_text}")
    print(response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
