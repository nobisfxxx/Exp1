from flask import Flask, request, jsonify

app = Flask(__name__)

# This is your webhook endpoint to receive Instagram webhook requests
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # If Instagram verifies your webhook, this code will handle the verification
    if request.method == 'GET':
        # Instagram will send a challenge in the form of a query parameter
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')

        # Verify the token sent by Instagram (your token from the Instagram setup)
        if verify_token == 'IGAAYMtqnh68pBZAFAxSlNkbHlCVnNxMTR2eWxNbVBMd2RUVC1jaWNPMmVlTW95WER1MkUtRDRudUxuMUxwcFJXRnVIblVxYjVYMzRfWVhFNk44N3hpdVp5cHVlMkpYdmc2aEJBLXg1SVo5dy1HWlRZAa0ZALSHZAFZAUMta3RuNUdyYwZDZD':
            return jsonify(challenge)
        else:
            return 'Verification failed', 403

    # Handle POST requests (this is where you will process incoming webhook data)
    if request.method == 'POST':
        data = request.json  # This is the data sent by Instagram
        print(data)  # You can log the data or process it as needed
        return 'Event received', 200


if __name__ == '__main__':
    # Run the Flask app on all available IPs
    app.run(host='0.0.0.0', port=5000, debug=True)
