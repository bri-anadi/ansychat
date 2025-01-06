from flask import Blueprint, jsonify, request, send_from_directory, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from typing import Tuple, Any
from services import UserService, MessageService
from exceptions import ValidationError, UnauthorizedAccessException, MessageNotFoundException
from models import User

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

@api.route('/api/messages', methods=['POST'])
@jwt_required()
def create_message() -> Tuple[Any, int]:
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400

        user = User.get_by_username(current_user)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        message = MessageService.create_message(user, data['content'])
        return jsonify(message.to_dict()), 201
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages/<int:message_id>', methods=['GET'])
@jwt_required()
def get_message(message_id: int) -> Tuple[Any, int]:
    try:
        message = MessageService.get_message_by_id(message_id)
        return jsonify(message.to_dict())
    except MessageNotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages/user', methods=['GET'])
@jwt_required()
def get_user_messages() -> Tuple[Any, int]:
    try:
        current_user = get_jwt_identity()
        messages = MessageService.get_user_messages(current_user)
        return jsonify([message.to_dict() for message in messages])
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages/search', methods=['GET'])
@jwt_required()
def search_messages() -> Tuple[Any, int]:
    try:
        query = request.args.get('q', '')
        messages = MessageService.search_messages(query)
        return jsonify([message.to_dict() for message in messages])
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def update_message(message_id: int) -> Tuple[Any, int]:
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        message = MessageService.update_message(message_id, data.get('content'), current_user)
        return jsonify(message.to_dict()), 200
    except UnauthorizedAccessException as e:
        return jsonify({'error': str(e)}), 403
    except MessageNotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id: int) -> Tuple[Any, int]:
    try:
        current_user = get_jwt_identity()
        MessageService.delete_message(message_id, current_user)
        return '', 204
    except UnauthorizedAccessException as e:
        return jsonify({'error': str(e)}), 403
    except MessageNotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Error deleting message: {str(e)}")
        return jsonify({'error': f"Server error: {str(e)}"}), 500