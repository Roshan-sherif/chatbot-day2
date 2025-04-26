from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # This enables CORS for all domains (for development only)

# Configuration - MUST REPLACE WITH YOUR VALID API KEY
TOGETHER_API_KEY = "1d0c05d5b4d30f43970a881aec5f90abf7dfa72bef2dfe6c3d076d8f3d814fec"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# Headers for Together API
HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

def query_together_api(prompt):
    """Helper function to query Together AI API"""
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stop": ["<|eot_id|>"]  # Required for Llama 3
    }
    
    try:
        response = requests.post(
            TOGETHER_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=10  # 10 second timeout
        )
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        
        # Parse the response
        data = response.json()
        return data['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {str(e)}")
        return None

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    # Get data from React frontend
    data = request.get_json()
    
    # Validate input
    if not data or 'message' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format. Please provide a "message" field.'
        }), 400
    
    user_message = data['message']
    chat_id = data.get('chat_id', 0)  # Optional chat ID
    
    # Get AI response
    ai_response = query_together_api(user_message)
    
    if ai_response is None:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get response from AI service',
            'chat_id': chat_id
        }), 500
    
    # Successful response
    return jsonify({
        'status': 'success',
        'response': ai_response,
        'chat_id': chat_id
    })

if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='0.0.0.0',  # Allows connections from other devices on network
        port=5000,
        debug=True,
        threaded=True  # Better for handling multiple requests
    )