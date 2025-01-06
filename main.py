from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from models import db
from routes import api
from socketio_handlers import SocketIOHandler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

    # Setup Socket.IO handlers
    socket_handler = SocketIOHandler(socketio)

    # Register blueprints
    swagger_ui = get_swaggerui_blueprint(
        Config.SWAGGER_URL,
        Config.API_URL,
        config={'app_name': "Chat Application API"}
    )
    app.register_blueprint(swagger_ui, url_prefix=Config.SWAGGER_URL)
    app.register_blueprint(api)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host="0.0.0.0")