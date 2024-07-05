from flask_jwt_extended import get_jwt
from flask_smorest import abort
from flask import jsonify
from functools import wraps


def get_claims():
    claims = get_jwt()
    return claims

# decorator that handle user priviliges
def user_allowed(role: str = "admin"):
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

def users_allowed(roles_list:list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = get_claims()['user_role']
            if user_role not in roles_list:
                abort(403, message='You are not authorized to access this route.')
            else:
                response = func(*args, **kwargs)
                return jsonify(response) 
        return wrapper
    return decorator
