from flask import Flask, request, jsonify
from rexeloft_llc import intelix
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "API Documentation": {
            "Credits": "This API is developed by Rexeloft LLC.",
            "/chat": {
                "method": "POST",
                "description": "Chat with the Intelix chatbot.",
                "request_format": {
                    "message": "User's message as a string.",
                    "plugins": {
                        "history": "Enable conversation history (true or false).",
                        "emotion": "Enable emotion detection (true or false)."
                    }
                },
                "example_request": {
                    "message": "What is the capital of India?",
                    "plugins": {
                        "history": True,
                        "emotion": False
                    }
                },
                "response_format": {
                    "response": "Chatbot response as a string.",
                    "emotion": "Detected emotion (if emotion plugin is enabled).",
                    "emotion_response": "Emotion-based response (if emotion plugin is enabled)."
                },
                "example_response": {
                    "response": "The capital of India is New Delhi."
                }
            }
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data or not isinstance(data['message'], str) or not data['message'].strip():
        return jsonify({'error': 'Message must be a non-empty string'}), 400

    message = data['message']
    plugins = data.get('plugins', {})

    try:
        response = intelix.chatbot_response(message)
        if plugins.get('emotion', False):
            emotion = intelix.detect_emotion(message)
            emotion_response = intelix.respond_based_on_emotion(emotion)
            return jsonify({
                'response': response,
                'emotion': emotion,
                'emotion_response': emotion_response
            })
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
