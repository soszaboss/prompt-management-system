from flask_smorest import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth', description='Operation sur la gestion des utilisateur')