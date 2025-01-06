from flask import Blueprint, jsonify, request, send_from_directory, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from typing import Tuple, Any
from services import UserService, MessageService
from exceptions import ValidationError

api = Blueprint('api', __name__)

@api.route('/static/swagger.yaml')
def send_swagger_file():
    return send_from_directory('static', 'swagger.yaml')

@api.route('/')
def home():
    return render_template('index.html')

@api.route('/api/check-username', methods=['POST'])
def check_username() -> Tuple[Any, int]:
    try:
        data = request.get_json()
        username = data.get('username')
        available, suggestions = UserService.check_username_availability(username)

        if not available:
            return jsonify({
                'available': False,
                'message': 'Username is already in use',
                'suggestions': suggestions
            }), 409

        return jsonify({'available': True, 'suggestions': []}), 200

    except ValidationError as e:
        return jsonify({
            'available': False,
            'message': str(e),
            'suggestions': []
        }), 400
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/login', methods=['POST'])
def login() -> Tuple[Any, int]:
    try:
        data = request.get_json()
        username = data.get('username')
        user = UserService.login_user(username)
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages() -> Tuple[Any, int]:
    try:
        messages = MessageService.get_all_messages()
        return jsonify([message.to_dict() for message in messages]), 200
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500