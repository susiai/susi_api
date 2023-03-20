import os, sys, argparse, logging, requests
from flask import Flask, jsonify, request, send_from_directory
from requests_toolbelt.multipart.encoder import MultipartEncoder
from waitress import serve

openai_api_key = ""

app = Flask(__name__)

# call i.e.:
# curl -X POST http://localhost:8080/api/audio/transcriptions -H "Content-Type: multipart/form-data" -F file="@test.wav" -F model="whisper-1"
@app.route('/api/audio/transcriptions', methods=['POST'])
def voice_recognition():
    if not openai_api_key:
        return jsonify({'error': 'No OpenAI API key provided'})

    audio_file = request.files['file']
    if audio_file:
        audio_data = audio_file.read()
        audio_name = audio_file.filename
        model = request.form.get('model', 'whisper-1')
        headers = {'Authorization': f'Bearer {openai_api_key}'}
        payload = MultipartEncoder(
            fields={
                "file": (audio_name, audio_data, "audio/x-wav"),
                "model": model
            }
        )
        headers["Content-Type"] = payload.content_type
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, data=payload)
        return jsonify(response.json())
    else:
        return jsonify({'error': 'No file provided'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load a model and save it as prepared model for finetuning")
    parser.add_argument("--port", default="8080", type=str, help="server port, default 8080")
    parser.add_argument("--host", default="0.0.0.0", type=str, help="bind address, default 0.0.0.0")
    parser.add_argument("--openai_api_key", default="", type=str, help="OpenAI API key")
    args = parser.parse_args()

    openai_api_key = args.openai_api_key
    
    # app.run(host='0.0.0.0') # development
    serve(app, host=args.host, port=args.port, threads=8)
