from app.votes import bp
from flask import jsonify
from flask_smorest import abort
from app.db import get_db
from app.votes.schemas import VoteSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed

# Endpoint pour gérer les votes
@bp.route('/vote/<int:id>')
class VoteView(MethodView):
    @bp.response(200, description='Get vote by id.')
    @jwt_required()
    def get(self, id):
        db = get_db()
        vote = db.execute(
            "SELECT\
            v.id,\
            v.vote,\
            u.username,\
            p.id AS prompt_id,\
            p.prompt\
            FROM votes v\
            JOIN users u ON v.user_id = u.id\
            JOIN prompts p ON v.prompt_id = p.id\
            WHERE v.id = %s;", (id,)
        ).fetchone()
        if vote is None:
            abort(404, message='Vote does not exist')
        return vote

    @bp.response(204, description='Vote successfully deleted.')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        try:
            db = get_db()
            vote = db.execute("SELECT * FROM votes WHERE id = %s;", (id,)).fetchone()
            if vote is None:
                abort(404, message='Vote does not exist')
            db.execute("DELETE FROM votes WHERE id = %s;", (id,))
            return '', 204
        except:
            abort(500, message='Try later...')

    @bp.arguments(VoteSchema, location='json', description='Update vote.', as_kwargs=True)
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, **kwargs):
        try:
            vote = kwargs.get('vote')
            prompt_id = kwargs.get('prompt_id', None)
            db = get_db()
            if vote and prompt_id:
                db.execute(
                            "UPDATE votes SET vote = %s, prompt_id = %s, updated_at = NOW() WHERE id = %s;",
                            (vote, prompt_id, id)
                        )
            elif vote and prompt_id is None:
                db.execute(
                            "UPDATE votes SET vote = %s, updated_at = NOW() WHERE id = %s;",
                            (vote, id)
                        )
            else:
                abort(400, message='Vote does not exist.')
        except:
            abort(500, message='Try later...')
        else:
            return jsonify({'message': 'Vote updated successfully'}), 200

@bp.route('/vote/add', methods=['POST'])
@bp.arguments(VoteSchema, location='json', description='Add vote.', as_kwargs=True)
@jwt_required()
def add_vote(**kwargs):
    try:
        db = get_db()
        vote = kwargs.get('vote')
        prompt_id = kwargs.get('prompt_id')
        user_id = int(get_jwt()['sub'])
        db.execute(
            "INSERT INTO votes (vote, prompt_id, user_id) VALUES (%s, %s, %s);",
            (vote, prompt_id, user_id)
        )
    except:
        abort(500, message='Try later...')
    return jsonify({'message': 'Vote added successfully'}), 201

@bp.route('/votes')
@jwt_required()
def get_votes():
    try:
        db = get_db()
        votes = db.execute("SELECT\
                            v.id,\
                            v.vote,\
                            u.username,\
                            p.id AS prompt_id,\
                            p.prompt\
                            FROM votes v\
                            JOIN users u ON v.user_id = u.id\
                            JOIN prompts p ON v.prompt_id = p.id;").fetchall()
        return jsonify(votes), 200
    except:
        abort(500, message='Try later...')


@bp.route('/prompt/<int:prompt_id>/vote', methods=['POST'])
@jwt_required()
def vote_for_prompt(prompt_id):
    db = get_db()
    user_id = int(get_jwt()['sub'])

    # Calculate the vote points
    points = db.execute("SELECT calculate_vote_points(%s, %s);", (user_id, prompt_id)).fetchone()[0]

    db.execute(
        "INSERT INTO votes (prompt_id, user_id, points) VALUES (%s, %s, %s);",
        (prompt_id, user_id, points)
    )

    # Check for prompt activation
    db.execute("SELECT check_prompt_activation(%s);", (prompt_id,))

    return jsonify({'message': 'Vote added successfully'}), 201