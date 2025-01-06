from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from typing import Dict, Any
from exceptions import UnauthorizedAccessException
from models import User
from services import MessageService

class SocketIOHandler:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.setup_handlers()

    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @self.socketio.on('join')
        def handle_join(data: Dict[str, Any]):
            try:
                username = data['username']
                user = User.get_by_username(username)
                if user:
                    user.set_online_status(True)
                join_room('chat_room')
                emit('user_joined', {'username': username}, room='chat_room')
            except Exception as e:
                print(f"Error in handle_join: {str(e)}")

        @self.socketio.on('leave')
        def handle_leave(data: Dict[str, Any]):
            try:
                username = data['username']
                user = User.get_by_username(username)
                if user:
                    user.set_online_status(False)
                leave_room('chat_room')
                emit('user_left', {'username': username}, room='chat_room')
            except Exception as e:
                print(f"Error in handle_leave: {str(e)}")

        @self.socketio.on('new_message')
        def handle_new_message(data: Dict[str, Any]):
            try:
                decoded_token = decode_token(data['token'])
                current_user = decoded_token['sub']

                if current_user != data['username']:
                    raise UnauthorizedAccessException("Token username mismatch")

                user = User.get_by_username(current_user)
                message = MessageService.create_message(user, data['content'])
                emit('message', message.to_dict(), room='chat_room')
            except Exception as e:
                print(f"Error in handle_new_message: {str(e)}")

        @self.socketio.on('edit_message')
        def handle_edit_message(data: Dict[str, Any]):
            try:
                decoded_token = decode_token(data['token'])
                current_user = decoded_token['sub']

                if current_user != data['username']:
                    raise UnauthorizedAccessException("Token username mismatch")

                message = MessageService.update_message(
                    data['messageId'],
                    data['content'],
                    current_user
                )

                emit('message_edited', {
                    'messageId': data['messageId'],
                    'content': data['content']
                }, room='chat_room')
            except Exception as e:
                print(f"Error in handle_edit_message: {str(e)}")

        @self.socketio.on('delete_message')
        def handle_delete_message(data: Dict[str, Any]):
            try:
                decoded_token = decode_token(data['token'])
                current_user = decoded_token['sub']

                if current_user != data['username']:
                    raise UnauthorizedAccessException("Token username mismatch")

                MessageService.delete_message(int(data['messageId']), current_user)
                emit('message_deleted', {'messageId': data['messageId']}, broadcast=True)
            except Exception as e:
                print(f"Error in handle_delete_message: {str(e)}")