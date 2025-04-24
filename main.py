from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "iamnobi"
PAGE_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("Sent message:", response.json())

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verified!")
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Received data:", data)

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    msg_data = change["value"]
                    sender_id = msg_data["sender"]["id"]
                    message_text = msg_data["message"]["text"]

                    print(f"Incoming message from {sender_id}: {message_text}")

                    # Send roast reply
                    roast_reply = f"@{sender_id} bhai tu chup reh... nobi bot active hai"
                    send_message(sender_id, roast_reply)

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
