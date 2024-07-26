import uuid
import datetime
import os
import dotenv

dotenv.load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    DATABASE = os.environ.get('CONNINFO')
    API_TITLE = os.environ.get('API_TITLE')
    API_VERSION = os.environ.get('API_VERSION')
    OPENAPI_VERSION = os.environ.get('OPENAPI_VERSION')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')



