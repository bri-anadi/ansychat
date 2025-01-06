from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from typing import List, Optional

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    messages = db.relationship('Message', backref='user', lazy=True)

    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        return cls.query.filter_by(username=username).first()

    @classmethod
    def create(cls, username: str) -> 'User':
        user = cls(username=username, is_online=True)
        db.session.add(user)
        db.session.commit()
        return user

    def set_online_status(self, status: bool) -> None:
        self.is_online = status
        db.session.commit()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id: int, username: str, content: str) -> 'Message':
        message = cls(user_id=user_id, username=username, content=content)
        db.session.add(message)
        db.session.commit()
        return message

    def update_content(self, content: str) -> None:
        self.content = content
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }