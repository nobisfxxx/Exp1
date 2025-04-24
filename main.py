from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Webhook POST received:", json.dumps(data, indent=2))

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messaging_product = value.get("messaging_product")
                sender_id = value.get("sender", {}).get("id")
                message_data = value.get("message", {})
                message_text = message_data.get("text")

                if message_text:
                    # You can add group-check logic here if needed
                    reply = "Oii massage maat kar warga nobi aa jaega 😡🪓🌶"
                    send_message(sender_id, reply)

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("Message sent:", response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
