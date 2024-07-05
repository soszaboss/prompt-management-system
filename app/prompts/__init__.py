from flask_smorest import Blueprint

bp = Blueprint('prompts', __name__, url_prefix='/prompts', description='Operations sur la gestion des prompts')

import app.prompts.views
