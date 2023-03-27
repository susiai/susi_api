from flask import Blueprint, jsonify, current_app

system_blueprint = Blueprint('system_service', __name__)

# signal that the application is ready
@system_blueprint.route('/api/system/ready.json')
def ready():
    return jsonify({'health': 'ok'})

