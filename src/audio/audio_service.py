import io, requests, tempfile
from flask import Blueprint, jsonify, request, current_app
from requests_toolbelt.multipart.encoder import MultipartEncoder
import whisper

audio_blueprint = Blueprint('audio_service', __name__)

# call i.e.:
# curl -X POST http://localhost:8080/api/audio/voice/transcriptions -H "Content-Type: multipart/form-data" -F file="@test.wav" -F model="whisper-1"
@audio_blueprint.route('/api/audio/voice/transcriptions', methods=['POST'])
def voice_recognition():
    openai_api_key = current_app.config['OPENAI_API_KEY']
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
