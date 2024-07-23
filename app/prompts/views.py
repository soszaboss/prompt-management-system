from app.prompts import bp
from flask import jsonify
from flask_smorest import abort
from app.db import get_db
from app.prompts.schemas import PromptSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed

# Endpoint pour gérer les prompts
@bp.route('/prompt/<int:id>')
class Prompt(MethodView):
    @bp.response(200, description='Get prompt by id.')
    @jwt_required()
    def get(self, id):
        db = get_db()
        prompt = db.execute(
           "SELECT\
            p.id,\
            p.prompt,\
            u.username,\
            s.id AS statut_id,\
            s.statut AS statut\
            FROM prompts p\
            JOIN users u ON p.user_id = u.id\
            JOIN statuts s ON p.statut_id = s.id\
            WHERE p.id = %s;", (id,)
        ).fetchone()
        if prompt is None:
            abort(404, message='Prompt does not exist')
        return prompt

    @bp.response(204, description='Prompt successfully deleted.')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        try:
            db = get_db()
            prompt = db.execute("SELECT * FROM prompts WHERE id = %s;", (id,)).fetchone()
            if prompt is None:
                abort(404, message='Prompt does not exist')
            db.execute("DELETE FROM prompts WHERE id = %s;", (id,))
            return '', 204
        except:
            abort(500, message='Try later...')

    @bp.arguments(PromptSchema, location='json', description='Update prompt.', as_kwargs=True)
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, **kwargs):
        try:
            prompt = kwargs.get('prompt')
            statut_id = kwargs.get('statut_id', None)
            prix = kwargs.get('prix', None)
            db = get_db()
            if prompt and statut_id:
                db.execute(
                            "UPDATE prompts SET prompt = %s, statut_id = %s, updated_at = NOW() WHERE id = %s;",
                            (prompt, statut_id, id)
                        )
            elif prompt and statut_id is None:
                db.execute(
                            "UPDATE prompts SET prompt = %s, updated_at = NOW() WHERE id = %s;",
                            (prompt, id)
                        )
            else:
                abort(400, message='Prompt does not exist.')
        except:
            abort(500, message='Try later...')
        else:
            return jsonify({'message': 'Prompt updated successfully'}), 200

# Endpoint pour afficher les prompts par statut
@bp.route('/status/<int:status_id>')
@jwt_required()
def get_prompts_by_status(status_id):
    try:
        db = get_db()
        prompts = db.execute(
                            "SELECT\
                            p.id,\
                            p.prompt,\
                            u.username,\
                            s.id AS statut_id,\
                            s.statut AS statut\
                            FROM prompts p\
                            JOIN users u ON p.user_id = u.id\
                            JOIN statuts s ON p.statut_id = s.id\
                            WHERE p.statut_id = %s;", (status_id,)
        ).fetchall()
        return jsonify(prompts), 200
    except:
        abort(404, message='Statut does not exist')

# Endpoint pour afficher les prompts par utilisateur
@bp.route('/user/<int:user_id>')
@jwt_required()
def get_prompts_by_user(user_id):
        db = get_db()
        try:
            prompts = db.execute("SELECT\
                                p.id,\
                                p.prompt,\
                                u.username,\
                                s.id AS statut_id,\
                                s.statut AS statut\
                                FROM prompts p\
                                JOIN users u ON p.user_id = u.id\
                                JOIN statuts s ON p.statut_id = s.id\
                                WHERE p.user_id = %s;", (user_id,)
            ).fetchall()
        except:
            abort(500, message='Try later...')
        else:
            print(prompts)
            if prompts:
                print('here')
                return jsonify(prompts), 200
            else:
                print('there')
                abort(404, message='User does not exist')


@bp.route('/prompt/add', methods=['POST'])
@bp.arguments(PromptSchema, location='json', description='Add prompt.', as_kwargs=True)
@jwt_required()
def add_prompt(**kwargs):
    try:
        db = get_db()
        prompt = kwargs.get('prompt')
        statut_id = kwargs.get('statut_id', 1)
        prix = kwargs.get('prix', 1000)
        user_id = int(get_jwt()['sub'])
        prompt = db.execute(
            "select create_and_get_prompt(%s, %s, %s, %s);",
            (prompt, user_id, prix, statut_id)
        )
        print(prompt)
    except:
        abort(500, message='Try later...')
    return jsonify({'message': 'Prompt added successfully'}), 201

@bp.route('/')
def get_prompts():
    try:
        db = get_db()
        prompts = db.execute("SELECT\
                            p.id,\
                            p.prompt,\
                            u.username,\
                            s.id AS statut_id,\
                            s.statut AS statut\
                            FROM prompts p\
                            JOIN users u ON p.user_id = u.id\
                            JOIN statuts s ON p.statut_id = s.id;").fetchall()
        return jsonify(prompts), 200
    except:
        abort(500, message='Try later...')

# Route pour gérer les statuts des prompts
@bp.route('/manage_status', methods=['POST'])
@jwt_required()
@user_allowed('admin')
def manage_status():
    db = get_db()
    db.execute("SELECT manage_prompt_status();")
    return jsonify({'message': 'Prompt statuses managed successfully'}), 200