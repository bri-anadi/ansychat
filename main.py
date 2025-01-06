# app.py
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token as jwt_decode_token
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import yaml
import os
import random
import string

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config[
    'JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Chat Application API",
        # Tambahkan konfigurasi CORS untuk Replit
        'swagger_ui_config': {
            'displayRequestDuration': True,
            'docExpansion': 'none'
        }
    })

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

db = SQLAlchemy(app)
jwt = JWTManager(app)
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    logger=True,
                    engineio_logger=True)

if not os.path.exists('static'):
    os.makedirs('static')


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_online = db.Column(db.Boolean,
                          default=False)  # Track user online status


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


def generate_username_suggestions(base_username):
    suggestions = []

    # Add number suffixes
    for i in range(1, 4):
        suggestion = f"{base_username}{i}"
        if not User.query.filter_by(username=suggestion,
                                    is_online=True).first():
            suggestions.append(suggestion)

    # Add random suffixes
    for _ in range(2):
        suffix = ''.join(random.choices(string.ascii_lowercase, k=2))
        suggestion = f"{base_username}_{suffix}"
        if not User.query.filter_by(username=suggestion,
                                    is_online=True).first():
            suggestions.append(suggestion)

    return suggestions[:3]  # Return max 3 suggestions


# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('join')
def handle_join(data):
    username = data['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_online = True
        db.session.commit()
    join_room('chat_room')
    emit('user_joined', {'username': username}, room='chat_room')


@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_online = False
        db.session.commit()
    leave_room('chat_room')
    emit('user_left', {'username': username}, room='chat_room')


@socketio.on('new_message')
def handle_new_message(data):
    username = data['username']
    content = data['content']
    token = data['token']

    try:
        decoded_token = jwt_decode_token(token)
        current_user = decoded_token['sub']

        if current_user != username:
            return

        user = User.query.filter_by(username=username).first()
        if user:
            new_message = Message(user_id=user.id,
                                  username=username,
                                  content=content)
            db.session.add(new_message)
            db.session.commit()

            emit('message', {
                'id': new_message.id,
                'username': username,
                'content': content,
                'timestamp': new_message.timestamp.isoformat()
            },
                 room='chat_room')
    except Exception as e:
        print(f"Error handling message: {str(e)}")


@socketio.on('edit_message')
def handle_edit_message(data):
    try:
        decoded_token = jwt_decode_token(data['token'])
        current_user = decoded_token['sub']

        if current_user != data['username']:
            return

        message = db.session.get(Message, data['messageId'])
        if message and message.username == current_user:
            message.content = data['content']
            db.session.commit()

            emit('message_edited', {
                'messageId': data['messageId'],
                'content': data['content']
            },
                 room='chat_room')
    except Exception as e:
        print(f"Error handling message edit: {str(e)}")


@socketio.on('delete_message')
def handle_delete_message(data):
    try:
        decoded_token = jwt_decode_token(data['token'])
        current_user = decoded_token['sub']

        if current_user != data['username']:
            return

        message_id = int(data['messageId'])
        message = db.session.get(Message, message_id)

        if message and message.username == current_user:
            db.session.delete(message)
            db.session.commit()

            print(f"Emitting message_deleted event for message {message_id}"
                  )  # Debug log
            emit(
                'message_deleted', {'messageId': message_id}, broadcast=True
            )  # Menggunakan broadcast=True untuk memastikan semua client menerima
            print(f"Event message_deleted emitted successfully")  # Debug log
    except Exception as e:
        print(f"Error in handle_delete_message: {str(e)}")


# Routes
@app.route('/static/swagger.yaml')
def send_swagger_file():
    return send_from_directory('static', 'swagger.yaml')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/check-username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username')

    if not username or len(username.strip()) == 0:
        return jsonify({
            'available': False,
            'message': 'Username cannot be empty',
            'suggestions': []
        }), 400

    user = User.query.filter_by(username=username).first()
    if user and user.is_online:
        suggestions = generate_username_suggestions(username)
        return jsonify({
            'available': False,
            'message': 'Username is already in use',
            'suggestions': suggestions
        }), 409
    elif user:
        return jsonify({'available': True, 'suggestions': []}), 200
    return jsonify({'available': True, 'suggestions': []}), 200


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')

    if not username or len(username.strip()) == 0:
        return jsonify({'error': 'Username cannot be empty'}), 400

    user = User.query.filter_by(username=username).first()

    # Check if user exists and is online
    if user and user.is_online:
        return jsonify({'error': 'Username is already in use'}), 409

    # If user doesn't exist, create new user
    if not user:
        user = User(username=username, is_online=True)
        db.session.add(user)
    else:
        user.is_online = True

    db.session.commit()

    # Create access token for the user
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200


@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    return jsonify([{
        'id': message.id,
        'username': message.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    } for message in messages]), 200


@app.route('/api/messages', methods=['POST'])
@jwt_required()
def create_message():
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400

    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_message = Message(user_id=user.id,
                          username=current_user,
                          content=data['content'])

    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        'id': new_message.id,
        'username': new_message.username,
        'content': new_message.content,
        'timestamp': new_message.timestamp.isoformat()
    }), 201


@app.route('/api/messages/<int:message_id>', methods=['GET'])
@jwt_required()
def get_message(message_id):
    message = Message.query.get_or_404(message_id)
    return jsonify({
        'id': message.id,
        'username': message.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    })


@app.route('/api/messages/user', methods=['GET'])
@jwt_required()
def get_user_messages():
    current_user = get_jwt_identity()
    messages = Message.query.filter_by(username=current_user).all()
    return jsonify([{
        'id': message.id,
        'username': message.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    } for message in messages])


@app.route('/api/messages/search', methods=['GET'])
@jwt_required()
def search_messages():
    query = request.args.get('q', '')
    messages = Message.query.filter(Message.content.like(f'%{query}%')).all()
    return jsonify([{
        'id': message.id,
        'username': message.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    } for message in messages])


@app.route('/api/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def update_message(message_id):
    current_user = get_jwt_identity()
    message = db.session.get(Message, message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    # Check if the user owns this message
    if message.username != current_user:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    message.content = data.get('content')
    db.session.commit()

    return jsonify({
        'id': message.id,
        'content': message.content,
        'username': message.username,
        'timestamp': message.timestamp.isoformat()
    }), 200


@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    try:
        current_user = get_jwt_identity()
        message = Message.query.get_or_404(message_id)

        if message.username != current_user:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(message)
        db.session.commit()

        print(f"Message {message_id} deleted via HTTP route"
              )  # Tambahkan log ini
        return '', 204
    except Exception as e:
        print(f"Error deleting message: {str(e)}")  # Tambahkan log ini
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host="0.0.0.0")
