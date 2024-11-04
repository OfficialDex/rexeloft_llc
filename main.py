from flask import Flask, request, jsonify
from rexeloft_llc import intelix

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Rexeloft-LLC Chatbot API. Use /chat to interact with the chatbot and /detect_emotion to analyze emotions."})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    history = data.get("history", True)

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = intelix.chatbot_response(user_input, use_history=history)
    return jsonify({"response": response})

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    emotion = intelix.detect_emotion(user_input)
    emotion_response = intelix.respond_based_on_emotion(emotion)
    return jsonify({"emotion": emotion, "emotion_response": emotion_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))
