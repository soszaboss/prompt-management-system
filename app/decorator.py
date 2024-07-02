from flask_jwt_extended import get_jwt
from .extensions import jwt
from .db import get_db
from flask_smorest import abort


def get_claims():
    claims = get_jwt()
    return claims

@jwt.additional_claims_loader
def make_additionnal_claim(identity):
    id = int(identity)
    db = get_db()
    user_role = db.execute("select get_user_by_id(%s);", (id,)).fetchone()['get_user_by_id'][2]
    context = {'user_role': user_role}
    return context

# decorator that handle user priviliges
def user_role(func):
    def wrapper(*args, **kwargs):
        role_authorized = kwargs.get('role')
        user_role = get_claims()['user_role']
        if not role_authorized == user_role:
            abort(400, message=f'Only {role_authorized} are authorized to access this.')
        else:
            func()
    return wrapper

# load user
@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    id = int(jwt_data['sub'])
    db = get_db()
    user = db.execute("select get_user_by_id(%s);", (id,)).fetchone()['get_user_by_id']
    return user if user else None