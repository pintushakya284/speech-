from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
translator = Translator()
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        audio_file = request.files['audio']
        audio_path = os.path.join('static', 'audio', f"{uuid.uuid4()}.wav")
        audio_file.save(audio_path)

        # Configure speech recognition with PocketSphinx for offline usage
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
            audio = recognizer.record(source)

            # Perform recognition
            text = recognize_sphinx(audio)
            return jsonify({'recognized_text': text})
    except Exception as e:
        return jsonify({'recognized_text': '', 'error': str(e)})

def recognize_sphinx(audio):
    try:
        text = recognizer.recognize_sphinx(audio)
        return text
    except sr.UnknownValueError:
        return ''
    except sr.RequestError as e:
        return str(e)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('lang', 'en')

    if not text:
        return jsonify({'translated_text': 'No text to translate'})

    try:
        translated_text = translator.translate(text, dest=target_lang).text
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'translated_text': 'Translation failed', 'error': str(e)})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')

    if not text:
        return jsonify({'error': 'No text to convert to speech'})

    try:
        tts = gTTS(text=text, lang=lang)
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join('static', 'audio', filename)
        tts.save(filepath)
        return jsonify({'audio_url': f'/static/audio/{filename}'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'audio'), exist_ok=True)
    app.run(debug=True)
