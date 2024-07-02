from app.authentification import bp
from flask import jsonify
from flask_smorest import abort
from app.messages import Message
from app.db import get_db
from .schema import UserSchema, LoginShema
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask.views import MethodView
import re
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


def validate_password(password):
    '''
        regex pattern that checks if a password meets the following requirements:

        At least 12 characters in length.
        Contains at least one uppercase letter.
        Contains at least one lowercase letter.
        Contains at least one digit (number).
        Contains at least one special character (e.g., !, @, #, $, %, etc.).
    '''
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&*])[A-Za-z\d@#$%^&*]{12,}$"
    return bool(re.match(pattern, password))

@bp.route('/register', methods=['POST'])
@bp.arguments(UserSchema, location='json', description='Registring user.', as_kwargs=True)
@bp.response(status_code=201, schema=Message, description='sending message after a registring attemp')
@jwt_required()
def register(**kwargs):
        username = kwargs.get("username").strip()
        email = kwargs.get("email").strip()
        password = kwargs.get("password").strip()
        confirm_password = kwargs.get("confirm_password").strip()
        if password != confirm_password:
            abort(409, message='Password not conforme')
        else:
            db = get_db()
            if db.execute("select *from users where email = %s;", (email,)).fetchone() is not None:
                abort(409, message='Email already used.')
            elif db.execute("select *from users where username = %s;", (username,)).fetchone() is not None:
                abort(409, message='Username already used.')
            else:
                if validate_password(password=password):
                    hashed_password = generate_password_hash(password=password)
                    db.execute("select create_get_user(%s, %s, %s, %s);", (username, email, hashed_password, 2)).fetchone()['create_get_user'][1::]
                    return jsonify(message='Account created successfully. Please check your email to activate your account.'), 201
                else:
                     abort(400, message="Invalid password format, Minimum length, uppercase, lowercase, digit, and special character.")

    
@bp.route('/login', methods=['POST'])
@bp.arguments(LoginShema, location='json', description='log an user.', as_kwargs=True)
@bp.response(status_code=201, schema=Message, description='sending message after a login attemp')
def login(**kwargs):
        email = kwargs.get("email")
        password = kwargs.get("password")
        db = get_db()
        user = db.execute("select *from users where email = %s;", (email,)).fetchone()
        print(user)
        if user is None:
            print('pas autorisé')
            abort(404, message='User does not exist.')
        else:
            hashed_password = user['password']
            check_password = check_password_hash( pwhash=hashed_password,password=password)
            if check_password:
                access_token = create_access_token(identity=user['id'], fresh=True)
                refresh_token = create_refresh_token(identity=user['id'])
                context = {
                     'tokens': {
                          'access': access_token,
                          'refresh': refresh_token
                     }
                }
                return jsonify(message=context), 200
            else:
                abort(401, message='Invalid password.')


@bp.route('/refresh-token', methods=['GET'])
@bp.response(status_code=200, schema=Message, description='sending message after rquest for new access token')
@jwt_required(refresh=True)
def refresh_token():
    id = int(get_jwt_identity())
    new_access_token = create_access_token(identity=id)
    return jsonify({'new_access_token':new_access_token}), 200

@bp.route('/logout', methods=['GET'])
@bp.response(status_code=200, schema=Message, description='logout user with a message')
@jwt_required(refresh=True)
def logout():
    db = get_db()
    jwt = get_jwt()
    jti = jwt['jti']
    db.execute("insert into tokens_block_list(jti) values (%s)", (jti,))
    return jsonify({'message': 'logout successfuly'}), 200

