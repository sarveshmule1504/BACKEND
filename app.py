import os
import base64
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# GROQ API Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "API is running!"})

@app.route('/classify', methods=['POST'])
def classify():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_data = image_file.read()

    # Convert to base64
    b64_image = base64.b64encode(image_data).decode('utf-8')

    # Prepare Groq Payload
    payload = {
        "model": MODEL,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Classify this waste into one of 4 categories: 1 for Hybrid, 2 for Sharp, 3 for Biodegradable, 4 for Infectious. Reply ONLY with the number (1, 2, 3, or 4)."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract the classification (1, 2, 3, or 4)
        reply = data['choices'][0]['message']['content'].strip()
        
        # Try to parse the integer safely
        try:
            classification = int(reply[0])
            if classification not in [1, 2, 3, 4]:
                classification = 1 # Fallback to Hybrid
        except:
            classification = 1 # Fallback to Hybrid

        return jsonify({"class": classification})
        
    except Exception as e:
        print(f"Error classifying: {e}")
        return jsonify({"error": str(e), "class": -1}), 500

if __name__ == '__main__':
    # Start the Flask app on port 5000 (bind to 0.0.0.0 for Render)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
