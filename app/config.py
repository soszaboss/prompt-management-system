import datetime
import os
import dotenv

dotenv.load_dotenv()

class Config:
    SECRET_KEY = "02b374365cb8418b972b269a9a18982f"
    JWT_SECRET_KEY = "4a6810c54e6d4ab59a6a3be0b3fbce9b"
    DATABASE = os.environ.get('CONNINFO')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    PROPAGATE_EXCEPTIONS = os.getenv('PROPAGATE_EXCEPTIONS')
    API_TITLE = os.getenv('API_TITLE')
    OPENAPI_VERSION = os.getenv('OPENAPI_VERSION')
    API_VERSION = os.getenv('API_VERSION')
    OPENAPI_JSON_PATH = os.getenv('OPENAPI_JSON_PATH')
    OPENAPI_URL_PREFIX = os.getenv('OPENAPI_URL_PREFIX')
    OPENAPI_REDOC_PATH = os.getenv('OPENAPI_REDOC_PATH')
    OPENAPI_REDOC_URL = os.getenv('OPENAPI_REDOC_URL')
    OPENAPI_SWAGGER_UI_PATH = os.getenv('OPENAPI_SWAGGER_UI_PATH')
    OPENAPI_SWAGGER_UI_URL = os.getenv('OPENAPI_SWAGGER_UI_URL')
    OPENAPI_RAPIDOC_PATH = os.getenv('OPENAPI_RAPIDOC_PATH')
    OPENAPI_RAPIDOC_URL = os.getenv('OPENAPI_RAPIDOC_URL')



