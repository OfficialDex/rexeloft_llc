from flask import Flask, request, jsonify
import json
import re
import requests
from googletrans import Translator
from fuzzywuzzy import fuzz
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from functools import lru_cache
from difflib import SequenceMatcher
import random
import nltk
import os

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)

dataset = {
    "Who owns you?": "I am owned by Rexeloft LLC",
    "Who created you?": "I was created in October 2024 by Rexeloft LLC"
}

synonyms = {
    "wtf": "what the fuck", "idk": "I don't know"
}

emotion_responses = {
    'happy': ["I'm glad to hear that!", "That's awesome!", "Yay!", "Very nice!"],
    'sad': ["I'm sorry to hear that.", "I hope things get better soon.", "Stay strong!", "Never give up!"],
    'angry': ["Take a deep breath.", "I apologize if I did something wrong.", "Sorry if I did anything wrong"],
    'neutral': ["Got it.", "Understood.", "Okay!", "Alright!", "Bet"]
}

api_url = "https://tilki.dev/api/hercai"
conversation_history = []
stemmer = PorterStemmer()

def trim_conversation_history():
    global conversation_history
    all_words = ' '.join(conversation_history).split()
    if len(all_words) > 70:
        trimmed_words = all_words[-70:]
        conversation_history = [' '.join(trimmed_words[i:i+10]) for i in range(0, len(trimmed_words), 10)]

def detect_language(text):
    translator = Translator()
    detection = translator.detect(text)
    return detection.lang

def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text

def translate_from_english(text, lang):
    translator = Translator()
    translation = translator.translate(text, dest=lang)
    return translation.text

@lru_cache(maxsize=1000)
def lemmatize_word(word):
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(word)

def replace_synonyms(text):
    words = text.split()
    replaced_words = [synonyms.get(word.lower(), word) for word in words]
    return ' '.join(replaced_words)

def normalize_and_lemmatize(text):
    text = text.lower()
    words = re.findall(r'\w+', text)
    lemmatized_words = [lemmatize_word(word) for word in words]
    return ' '.join(lemmatized_words)

def get_word_similarity(word1, word2):
    return SequenceMatcher(None, word1, word2).ratio()

def get_most_similar_question(question):
    questions = list(dataset.keys())
    if not questions:
        return None

    question_words = question.lower().split()
    expanded_question = set(stemmer.stem(word) for word in question_words)

    highest_ratio = 0
    most_similar_question = None

    for q in questions:
        q_words = q.lower().split()
        expanded_q = set(stemmer.stem(word) for word in q_words)

        common_words = expanded_question.intersection(expanded_q)
        similarity_ratio = len(common_words) / len(expanded_question.union(expanded_q))

        fuzzy_ratio = fuzz.token_set_ratio(question, q) / 100
        word_similarity = sum(get_word_similarity(w1, w2) for w1 in expanded_question for w2 in expanded_q) / (len(expanded_question) * len(expanded_q))

        combined_score = (similarity_ratio + fuzzy_ratio + word_similarity) / 3
        if combined_score > highest_ratio:
            highest_ratio = combined_score
            most_similar_question = q

    if highest_ratio > 0.5:
        return most_similar_question
    return None

def detect_emotion(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    compound_score = sentiment_scores['compound']

    if compound_score >= 0.25:
        return 'happy'
    elif compound_score <= -0.25:
        return 'angry' if compound_score <= -0.5 else 'sad'
    else:
        return 'neutral'

def respond_based_on_emotion(emotion):
    return random.choice(emotion_responses[emotion])

def query_external_api(question):
    try:
        params = {'soru': question}
        print(f"Querying external API with URL: {api_url} and parameters: {params}")
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            result = response.json()
            print(f"Received successful response from API: {result}")
            return result.get('cevap')
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"RequestException encountered: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        print(f"Response content that failed to decode: {response.content}")
        return None
    except Exception as e:
        print(f"Unexpected error querying API: {e}")
        return None

def should_store_question(question):
    keywords = ["which", "who", "when", "how", "explain", "define"]
    return any(keyword in question.lower() for keyword in keywords)

def answer_question(question):
    normalized_question = normalize_and_lemmatize(replace_synonyms(question))
    similar_question = get_most_similar_question(normalized_question)

    if similar_question:
        return dataset[similar_question]
    else:
        return None

def chatbot_response(user_input, use_history, use_emotion):
    global conversation_history

    dataset_answer = answer_question(user_input)

    if dataset_answer:
        if use_history:
            conversation_history.append(f"You: {user_input}")
            conversation_history.append(f"Bot: {dataset_answer}")
            trim_conversation_history()
        return dataset_answer

    if use_history:
        conversation_history.append(f"You: {user_input}")
        history_string = "\n".join(conversation_history)
    else:
        history_string = user_input

    api_response = query_external_api(history_string)
    if api_response and should_store_question(user_input):
        dataset[normalize_and_lemmatize(user_input)] = api_response[:len(api_response)//2] if len(api_response) > 200 else api_response

    if use_history:
        conversation_history.append(f"Bot: {api_response if api_response else 'I don’t have an answer.'}")
        trim_conversation_history()
    return api_response if api_response else "I'm sorry, I don't have an answer for that."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided. Please send a JSON payload with 'message'."}), 400
    user_input = data.get('message')
    plugins = data.get('plugins', {})

    if not user_input:
        return jsonify({"error": "No 'message' provided in JSON payload."}), 400

    use_history = plugins.get("history", False)
    use_emotion = plugins.get("emotion", False)

    emotion_response = ""
    if use_emotion:
        emotion = detect_emotion(user_input)
        emotion_response = respond_based_on_emotion(emotion)

    response = chatbot_response(user_input, use_history, use_emotion)
    return jsonify({
        "emotion_response": emotion_response if use_emotion else None,
        "bot_response": response
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
