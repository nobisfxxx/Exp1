from flask import Flask, request
import os

app = Flask(__name__)

# Get VERIFY_TOKEN from Railway environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "iamnobi")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification from Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        # Handle actual incoming messages (optional)
        data = request.json
        print("Received webhook:", data)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    # Run on the correct port for Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
