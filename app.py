from flask import Flask, request, jsonify
import whisper
import io
import soundfile as sf
import numpy as np
import tempfile
import os
from scipy.io import wavfile
import string
import json
from flask_cors import CORS
import random
# from flask_ngrok import run_with_ngrok

model = whisper.load_model("tiny")

app = Flask(__name__)
CORS(app)

# Read questions from the JSON file
with open('questions.json') as f:
    questions_json = json.load(f)


def log(question,resp):
    with open('log.txt', 'a') as f:
        
        f.write(f"{question} : {resp}\n")


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file part'})

    audio_file = request.files['audio_data'].read()
    count = request.form['count']
    question = request.form['question']
    try:
        count = int(count)
    except ValueError:
        return jsonify({'error': 'Invalid count'})

    
    # print(count)
    # print(type(count))

    if count > 3:
        #log as invalid
        log(question,"Invalid response")

        

    
    if audio_file:
        with open("temp.wav", "wb") as fh:
            fh.write(audio_file)

    result = model.transcribe("temp.wav")
    res = result["text"]
    # Delete the temporary file
    os.remove("temp.wav")
    # Split into words
    words = res.split()

    # Remove punctuations
    word_list = [''.join(char for char in word if char not in string.punctuation) for word in words]

    # Remove empty strings (which might occur if a word was entirely punctuation)
    res = [word.lower() for word in word_list if word]

    
    print(word_list)

    if len(res) > 1:
        return jsonify({'message': "invalid"})
    else:
        res = res[0]
        if res.lower() == "no":
            log(question,"No")
            return jsonify({'message': "no"})
        elif res.lower() == "yes":
            log(question,"Yes")
            return jsonify({'message': "yes"})
        else:
            return jsonify({'message': res})

    return jsonify({'message': result["text"]})

@app.route('/get_question', methods=['GET'])
def get_random_question():
    # Select a random question from the JSON
    random_question = random.choice(questions_json)
    return jsonify(random_question)

@app.route('/', methods=['GET'])
def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask HTML Example</title>
    </head>
    <body>
        <h1>Hello from Flask!</h1>
        <p>This is a basic HTML page returned by a Flask route.</p>
    </body>
    </html>
    """
    return html_content



if __name__ == '__main__':
    app.run()
