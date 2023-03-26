import io, os, sys, argparse, logging, requests, tempfile
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from requests_toolbelt.multipart.encoder import MultipartEncoder
from waitress import serve
import whisper

openai_api_key = ""
app = Flask(__name__)
CORS(app)

# call i.e.:
# curl http://localhost:8080/api/text/chat/completions -H "Content-Type: application/json" -d '{"model": "gpt-3.5-turbo","messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}]}'
@app.route('/api/text/chat/completions', methods=['POST'])
def generate_completion():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'})

    messages = data.get('messages')
    if not messages:
        return jsonify({'error': 'No messages provided'})

    if not openai_api_key:
        return jsonify({'error': 'No OpenAI API key provided'})

    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'messages': messages,
        'model': 'gpt-3.5-turbo',
        'temperature': 1.0,
        'max_tokens': 50
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return jsonify(response.json())


# call i.e.:
# curl -X POST http://localhost:8080/api/audio/voice/transcriptions -H "Content-Type: multipart/form-data" -F file="@test.wav" -F model="whisper-1"
@app.route('/api/audio/voice/transcriptions', methods=['POST'])
def voice_recognition():
    if not request.files:
        return jsonify({'error': 'No file provided'})
    
    audio_file = request.files['file']
    audio_data = audio_file.read()
    audio_name = audio_file.filename
    model_name = request.form.get('model', 'tiny')
    result = {}

    if openai_api_key and model_name == 'whisper-1':
        headers = {'Authorization': f'Bearer {openai_api_key}'}
        payload = MultipartEncoder(
            fields={
                "file": (audio_name, io.BytesIO(audio_data), "audio/x-wav"),
                "model": model_name
            }
        )
        headers["Content-Type"] = payload.content_type
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, data=payload)
        result = response.json()
    else:
        # patch model name in case no api key is present
        if model_name == 'whisper-1': model_name = 'tiny'

        # Load the offline model
        model = whisper.load_model(model_name)

        # Save the received audio file temporarily to disk
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file.flush()

            # Transcribe using the offline model
            result = model.transcribe(temp_audio_file.name)

        result = {'text': result['text']}
        
    return result

# run this program with
# python3 src/main.py --openai_api_key <apikey>
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load a model and save it as prepared model for finetuning")
    parser.add_argument("--port", default="8080", type=str, help="server port, default 8080")
    parser.add_argument("--host", default="0.0.0.0", type=str, help="bind address, default 0.0.0.0")
    parser.add_argument("--openai_api_key", default=os.environ.get('OPENAI_API_KEY'), type=str, help="OpenAI API key")
    args = parser.parse_args()

    openai_api_key = args.openai_api_key
    
    # app.run(host='0.0.0.0') # development
    serve(app, host=args.host, port=args.port, threads=8)
