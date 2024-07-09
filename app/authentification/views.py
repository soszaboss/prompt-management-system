from app.authentification import bp
from flask import jsonify, request
from flask_smorest import abort
from app.messages import Message
from app.db import get_db, validate_password
from .schema import UserSchema, LoginShema
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.send_email import send_activation_email




@bp.route('/register', methods=['POST'])
@bp.arguments(UserSchema, location='json', description='Registring user.', as_kwargs=True)
@bp.response(status_code=201, schema=Message, description='sending message after a registring attemp')
# @jwt_required()
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
                    user = db.execute("select create_get_user(%s, %s, %s, %s);", (username, email, hashed_password, 2)).fetchone()['create_get_user']
                    user_id = int(user[0])
                    domain = request.url_root
                    print(f'this is the domain: {domain}')
                    send_activation_email(user_id=user_id, email=email)
                    return jsonify(message='Account created successfully. Please check your email to activate your account or your account will be automatically deleted in 15 minuites.'), 201
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
        if user is None:
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
@jwt_required()
def logout():
    db = get_db()
    jti = get_jwt()['jti']
    db.execute("insert into tokens_block_list(jti) values (%s)", (jti,))
    return jsonify({'message': 'logout successfuly'}), 200


@bp.route('/activate/<token>', methods=['GET'])
def activate(token):
    db = get_db()
    try:
        id = int(decode_token(token)['sub'])
        try:
            user = db.execute("select get_user_by_id(%s);", (id,)).fetchone()['get_user_by_id']
        except:
            user = None
        if user is not None:
            db.execute("UPDATE users SET is_activated = TRUE WHERE id = %s;", (id,))
            return jsonify(message="Account activated successfully."), 200
        else:
            return jsonify(message="Invalid activation link."), 400
    except Exception as e:
        return jsonify(message="Activation link expired or invalid."), 400