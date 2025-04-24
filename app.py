from flask import Flask, request, jsonify

app = Flask(__name__)

# Webhook verification route
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # This will verify your webhook with Instagram/Facebook
    # Replace with your secret verification token
    VERIFY_TOKEN = 'IGAAYMtqnh68pBZAFAxSlNkbHlCVnNxMTR2eWxNbVBMd2RUVC1jaWNPMmVlTW95WER1MkUtRDRudUxuMUxwcFJXRnVIblVxYjVYMzRfWVhFNk44N3hpdVp5cHVlMkpYdmc2aEJBLXg1SVo5dy1HWlRZAa0ZALSHZAFZAUMta3RuNUdyYwZDZD'
    
    # When Facebook sends the verification request, it will include a 'hub.verify_token' parameter
    # Check if it matches your secret token
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return 'Invalid verification token', 403

# Webhook to receive events (like messages, etc.)
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    print(data)  # Print the incoming webhook data
    # Process the data as needed
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
