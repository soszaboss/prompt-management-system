from app.authentification import bp
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from app.messages import Message
from app.db import get_db

from werkzeug.security import check_password_hash, generate_password_hash

class User(MethodView):

    def post():
        pass

    def get():
        pass

    def put():
        pass

    def delete():
        pass