from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_mail import Mail

jwt = JWTManager()

api = Api(spec_kwargs={})

mail = Mail()