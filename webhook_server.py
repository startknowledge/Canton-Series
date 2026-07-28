from flask import Flask, request, jsonify
import subprocess
import os
import json
import hmac
import hashlib

app = Flask(__name__)

# 🔐 यहाँ अपना Secret डालें (बिल्कुल वही जो GitHub पर डाला है)
SECRET = "MySuperSecret749"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # 1. चेक करें कि यह Push Event तो है?
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return jsonify({"message": "Ignored, not a push event"}), 200

    # 2. 🔐 GitHub Signature Verify करें (सुरक्षा के लिए)
    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        return 'Signature missing', 401
    
    # अपना खुद का Signature Calculate करें
    payload = request.get_data()  # Raw Body (Bytes)
    expected_signature = 'sha256=' + hmac.new(
        SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # दोनों Signatures Compare करें (Timing Attack से बचने के लिए hmac.compare_digest use करें)
    if not hmac.compare_digest(expected_signature, signature_header):
        return 'Invalid signature', 401

    print("✅ GitHub Push received and Verified! Running auto_deploy.sh...")
    
    try:
        # 3. आपकी auto_deploy.sh Script को Call करें
        result = subprocess.run(
            ['/home/ubuntu/auto_deploy.sh'], 
            capture_output=True, 
            text=True,
            timeout=300  # 5 मिनट का Timeout
        )
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        return jsonify({"status": "Deploy triggered successfully!"}), 200
        
    except Exception as e:
        print("❌ Error running script:", str(e))
        return jsonify({"status": "Failed", "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return "Webhook Server is Running with SECURE Signature!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
