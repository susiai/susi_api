import io, requests, tempfile
import wave
from flask import jsonify, request, current_app
from flask_restx import Namespace, Resource
from requests_toolbelt.multipart.encoder import MultipartEncoder
import whisper
from vosk import Model, KaldiRecognizer, SetLogLevel

api = Namespace('api/audio', description='text operations')

@api.route('/voice/transcriptions', methods=['POST'])
class VoiceTranscription(Resource):

    # call i.e.:
    # curl -X POST http://localhost:8080/api/audio/voice/transcriptions -H "Content-Type: multipart/form-data" -F file="@test.wav" -F model="whisper-1"
    @api.doc('voice_transcriptions')
    def post(self):
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
            # make an offline transcription

            # patch model name in case no api key is present
            if model_name == 'whisper-1': model_name = 'tiny'

            # check the required technology (whisper or vosk)
            if model_name == 'tiny' or model_name == 'base' or model_name == 'small' or model_name == 'medium' or model_name == 'large': 

                # Load the offline model
                model = whisper.load_model(model_name)

                # Save the received audio file temporarily to disk
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio_file:
                    temp_audio_file.write(audio_data)
                    temp_audio_file.flush()

                    # Transcribe using the offline model
                    result = model.transcribe(temp_audio_file.name)

                result = {'text': result['text']}

            if model_name == 'en-us' or model_name == 'de': 
                # use vosk transcriptions

                wf = wave.open(io.BytesIO(audio_data), "rb")
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    return jsonify({'error': 'Audio file must be WAV format mono PCM.'})

                model = Model('en-us')
                rec = KaldiRecognizer(model, wf.getframerate())
                rec.SetWords(True)
                rec.SetPartialWords(True)
                
                transcript = ""

                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        result = rec.Result()
                        transcript += result["text"]
                    else:
                        partial_result = rec.PartialResult()
                        if partial_result:
                            transcript += partial_result["partial"]

                result = {'text': transcript}
                    
        return result