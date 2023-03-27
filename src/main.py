import sys
sys.path.insert(0, './src')

import os, argparse
from flask import Flask
from waitress import serve
from flask_cors import CORS
from text.text_service import text_blueprint
from audio.audio_service import audio_blueprint
from system.system_service import system_blueprint

openai_api_key = ""
app = Flask(__name__)
CORS(app)

app.register_blueprint(text_blueprint)
app.register_blueprint(audio_blueprint)
app.register_blueprint(system_blueprint)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load a model and save it as prepared model for finetuning")
    parser.add_argument("--port", default="8080", type=str, help="server port, default 8080")
    parser.add_argument("--host", default="0.0.0.0", type=str, help="bind address, default 0.0.0.0")
    parser.add_argument("--openai_api_key", default=os.environ.get('OPENAI_API_KEY'), type=str, help="OpenAI API key")
    args = parser.parse_args()

    openai_api_key = args.openai_api_key
    app.config['OPENAI_API_KEY'] = openai_api_key

    serve(app, host=args.host, port=args.port, threads=8)
