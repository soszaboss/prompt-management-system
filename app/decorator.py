from flask_jwt_extended import get_jwt
from .extensions import jwt
from .db import get_db
from flask_smorest import abort
from flask import jsonify


def get_claims():
    claims = get_jwt()
    return claims

# decorator that handle user priviliges
def user_role(role: str = "admin"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_role = get_claims()['user_role']
            if not role == user_role:
                abort(400, message=f'Only {role} are authorized to access this.')
            else:
                response = func(*args, **kwargs)
                return jsonify(response) 
        return wrapper
    return decorator

