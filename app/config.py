import uuid
import datetime
import os
import dotenv

dotenv.load_dotenv()

class Config:
    SECRET_KEY = "02b374365cb8418b972b269a9a18982f"
    JWT_SECRET_KEY = "4a6810c54e6d4ab59a6a3be0b3fbce9b"
    DATABASE = os.environ.get('CONNINFO')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "soszabosssosza@gmail.com"
    MAIL_PASSWORD = "vsmd qrbz ywuz zbcc"
    MAIL_DEFAULT_SENDER = "soszabosssosza@gmail.com"
    PROPAGATE_EXCEPTIONS=True
    API_TITLE="Prompts API Management"
    OPENAPI_VERSION="3.0.2"
    API_VERSION="3.0.2"
    OPENAPI_JSON_PATH="api-spec.json"
    OPENAPI_URL_PREFIX="/"
    OPENAPI_REDOC_PATH="/redoc"
    OPENAPI_REDOC_URL=(
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH="/swagger-ui"
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH="/rapidoc"
    OPENAPI_RAPIDOC_URL="https://unpkg.com/rapidoc/dist/rapidoc-min.js"



