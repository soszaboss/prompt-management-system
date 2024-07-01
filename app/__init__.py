from .config import Config
from .extensions import api, jwt

from flask import Flask

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
    
    return app