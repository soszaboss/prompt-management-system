from flask_smorest import Blueprint

bp = Blueprint('users', __name__, url_prefix='/users', description='Operation sur la gestion des utilisateur')

import app.users.views