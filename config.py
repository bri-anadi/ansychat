class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'yo-ndak-tau-tanya-kok-tanya-saya'
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.yaml'