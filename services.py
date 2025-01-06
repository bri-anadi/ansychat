import random
import string
from typing import List, Optional
from models import User, Message, db
from exceptions import ValidationError, MessageNotFoundException, UnauthorizedAccessException

class UserService:
    @staticmethod
    def generate_username_suggestions(base_username: str) -> List[str]:
        suggestions = []

        # Generate numeric suggestions
        for i in range(1, 4):
            suggestion = f"{base_username}{i}"
            if not User.query.filter_by(username=suggestion, is_online=True).first():
                suggestions.append(suggestion)

        # Generate random suffix suggestions
        for _ in range(2):
            suffix = ''.join(random.choices(string.ascii_lowercase, k=2))
            suggestion = f"{base_username}_{suffix}"
            if not User.query.filter_by(username=suggestion, is_online=True).first():
                suggestions.append(suggestion)

        return suggestions[:3]

    @staticmethod
    def check_username_availability(username: str) -> tuple[bool, List[str]]:
        if not username or len(username.strip()) == 0:
            raise ValidationError("Username cannot be empty")

        user = User.get_by_username(username)
        if user and user.is_online:
            suggestions = UserService.generate_username_suggestions(username)
            return False, suggestions
        return True, []

    @staticmethod
    def login_user(username: str) -> User:
        if not username or len(username.strip()) == 0:
            raise ValidationError("Username cannot be empty")

        user = User.get_by_username(username)
        if user and user.is_online:
            raise ValidationError("Username is already in use")

        if not user:
            user = User.create(username)
        else:
            user.set_online_status(True)

        return user

class MessageService:
    @staticmethod
    def get_all_messages() -> List[Message]:
        return Message.query.order_by(Message.timestamp).all()

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[Message]:
        message = Message.query.get(message_id)
        if not message:
            raise MessageNotFoundException(f"Message {message_id} not found")
        return message

    @staticmethod
    def create_message(user: User, content: str) -> Message:
        if not content:
            raise ValidationError("Message content cannot be empty")
        return Message.create(user.id, user.username, content)

    @staticmethod
    def update_message(message_id: int, content: str, current_user: str) -> Message:
        message = MessageService.get_message_by_id(message_id)
        if message.username != current_user:
            raise UnauthorizedAccessException("Not authorized to edit this message")

        if not content:
            raise ValidationError("Message content cannot be empty")

        message.update_content(content)
        return message

    @staticmethod
    def delete_message(message_id: int, current_user: str) -> None:
        message = MessageService.get_message_by_id(message_id)
        if message.username != current_user:
            raise UnauthorizedAccessException("Not authorized to delete this message")

        db.session.delete(message)
        db.session.commit()

    @staticmethod
    def search_messages(query: str) -> List[Message]:
        return Message.query.filter(Message.content.like(f'%{query}%')).all()