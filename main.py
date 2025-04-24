from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Get tokens from environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("Incoming:", data)

        if "entry" in data:
            for entry in data["entry"]:
                if "messaging" in entry:
                    for msg_event in entry["messaging"]:
                        sender_id = msg_event["sender"]["id"]
                        if "message" in msg_event:
                            send_message(sender_id, "@sender Oii massage maat kar warga nobi aa jaega 😡🪓🌶")

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload)
    print("Sent:", response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
