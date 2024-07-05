from flask_smorest import Blueprint

bp = Blueprint('groupes', __name__, url_prefix='/groupes', description='Operations sur la gestion des groupes')

import app.groupes.views
