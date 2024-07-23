from flask_smorest import Blueprint

bp = Blueprint('votes', __name__, url_prefix='/votes', description='Gestion des votes')

import app.votes.views
