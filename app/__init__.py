from .config import Config
from .extensions import api, jwt
from .db import get_db
from flask import Flask, jsonify

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    api.init_app(app)
    jwt.init_app(app)

    from . import db
    db.init_app(app)


    # Adding the authentification blueprint 
    from app.authentification import bp as authentification
    api.register_blueprint(authentification)

    # Adding users implementations
    from app.users import bp as users
    api.register_blueprint(users)
    
    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header,jwt_data):
        jti = jwt_data['jti']
        db = get_db()
        token = db.execute("select get_jti_or_none(%s)", (jti,)).fetchone()['get_jti_or_none']
        # token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

        return token is not None

    return app