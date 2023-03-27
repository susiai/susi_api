import requests
from flask import Blueprint, jsonify, request, current_app

text_blueprint = Blueprint('text_service', __name__)

# call i.e.:
# curl http://localhost:8080/api/text/chat/completions -H "Content-Type: application/json" -d '{"model": "gpt-3.5-turbo","messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}]}'
@text_blueprint.route('/api/text/chat/completions', methods=['POST'])
def generate_completion():
    openai_api_key = current_app.config['OPENAI_API_KEY']
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

