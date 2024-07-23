from flask_smorest import Blueprint

bp = Blueprint('notes', __name__, url_prefix='/notes', description='Gestion des notes')

import app.notes.views
