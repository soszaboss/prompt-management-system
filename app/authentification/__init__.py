from flask_smorest import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth', description='Handle users authentification')

import app.authentification.views