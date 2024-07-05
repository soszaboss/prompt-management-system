from app.prompts import bp
from flask import jsonify
from flask_smorest import abort
from app.db import get_db
from app.prompts.schema import PromptSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.decorators import user_allowed

# Endpoint pour gérer les prompts
@bp.route('/<int:id>')
class Prompt(MethodView):
    @bp.response(200, PromptSchema)
    @jwt_required()
    def get(self, id):
        db = get_db()
        prompt = db.execute(
            "SELECT p.id, p.prompt, s.statut, u.username "
            "FROM prompts p "
            "JOIN statuts s ON p.statut_id = s.id "
            "JOIN users u ON p.user_id = u.id "
            "WHERE p.id = %s;", (id,)
        ).fetchone()
        if prompt is None:
            abort(404, message='Prompt does not exist')
        return prompt

    @bp.arguments(PromptSchema)
    @bp.response(201, PromptSchema)
    @jwt_required()
    def post(self, new_prompt):
        db = get_db()
        db.execute(
            "INSERT INTO prompts (prompt, user_id, statut_id) VALUES (%s, %s, %s);",
            (new_prompt['prompt'], new_prompt['user_id'], new_prompt['statut_id'])
        )
        return new_prompt, 201

    @bp.response(204, description='Prompt successfully deleted')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        db = get_db()
        prompt = db.execute("SELECT * FROM prompts WHERE id = %s;", (id,)).fetchone()
        if prompt is None:
            abort(404, message='Prompt does not exist')
        db.execute("DELETE FROM prompts WHERE id = %s;", (id,))
        return '', 204

    @bp.arguments(PromptSchema)
    @bp.response(200, PromptSchema)
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, updated_prompt):
        db = get_db()
        db.execute(
            "UPDATE prompts SET prompt = %s, statut_id = %s, updated_at = NOW() WHERE id = %s;",
            (updated_prompt['prompt'], updated_prompt['statut_id'], id)
        )
        return updated_prompt

# Endpoint pour afficher les prompts par statut
@bp.route('/status/<int:status_id>')
@bp.response(200, PromptSchema(many=True))
@jwt_required()
def get_prompts_by_status(status_id):
    db = get_db()
    prompts = db.execute(
        "SELECT p.id, p.prompt, s.statut, u.username "
        "FROM prompts p "
        "JOIN statuts s ON p.statut_id = s.id "
        "JOIN users u ON p.user_id = u.id "
        "WHERE p.statut_id = %s;", (status_id,)
    ).fetchall()
    return prompts

# Endpoint pour afficher les prompts par utilisateur
@bp.route('/user/<int:user_id>')
@bp.response(200, PromptSchema(many=True))
@jwt_required()
def get_prompts_by_user(user_id):
    db = get_db()
    prompts = db.execute(
        "SELECT p.id, p.prompt, s.statut, u.username "
        "FROM prompts p "
        "JOIN statuts s ON p.statut_id = s.id "
        "JOIN users u ON p.user_id = u.id "
        "WHERE p.user_id = %s;", (user_id,)
    ).fetchall()
    return prompts
