import uuid

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