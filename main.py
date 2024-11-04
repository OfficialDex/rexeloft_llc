import logging
from flask import Flask, jsonify, request
from rexeloft_llc import intelix
import os

app = Flask(__name__)
app.config['DEBUG'] = True

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Rexeloft LLC's Chatbot Ai (Intelix)"}), 200

@app.route('/chat', methods=['POST'])
def chat_response():
    data = request.json
    logging.debug(f"Received data for /chat: {data}")
    
    user_input = data.get('message')
    history_enabled = data.get('history', False)

    if not user_input:
        logging.error("No message input provided.")
        return jsonify({"error": "Message input is required"}), 400
    
    response = intelix.chatbot_response(user_input)
    logging.debug(f"Chatbot response: {response}")

    if history_enabled:
        conversation_history = intelix.conversation_history if intelix.conversation_history else []
        logging.debug(f"Conversation history: {conversation_history}")
        return jsonify({"response": response, "conversation_history": conversation_history})
    
    return jsonify({"response": response})

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.json
    logging.debug(f"Received data for /detect_emotion: {data}")

    user_input = data.get('message')
    if not user_input:
        logging.error("No message input provided.")
        return jsonify({"error": "Message input is required"}), 400
    
    emotion = intelix.detect_emotion(user_input)
    emotion_response = intelix.respond_based_on_emotion(emotion)
    logging.debug(f"Emotion detected: {emotion}, Emotion response: {emotion_response}")
    
    return jsonify({"emotion": emotion, "emotion_response": emotion_response})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
