from app.votes import bp
from flask import jsonify
from flask_smorest import abort
from app.db import get_db
from app.votes.schemas import VoteSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed, users_allowed

# Endpoint pour gérer les votes
@bp.route('/vote/<int:id>')
class VoteView(MethodView):
    @bp.response(200, description='Get vote by id.')
    @jwt_required()
    @user_allowed(['admin', 'user'])
    def get(self, id):
        db = get_db()
        vote = db.execute(
            "SELECT\
            v.id,\
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


@bp.route('/add/vote', methods=['POST'])
@bp.arguments(VoteSchema, location='json', description='Add vote.', as_kwargs=True)
@jwt_required()
def add_vote(**kwargs):
    db = get_db()
    prompt_id = kwargs.get('prompt_id')
    user_id = int(get_jwt()['sub'])
    prompt = db.execute("SELECT * FROM prompts WHERE id = %s;", (prompt_id,)).fetchone()
    if prompt is None:
        abort(404, message='Prompt does not exist')
    vote = db.execute("select id from votes where prompt_id = %s and user_id = %s;", (prompt_id, user_id))
    if vote.fetchone() is not None:
        abort(400, message='You have already voted for this prompt.')
    try:
        print('point')
        points = db.execute("SELECT calculate_vote_points(%s, %s);", (user_id, prompt_id)).fetchone()['calculate_vote_points']
        print(f'points: {points}')
        db.execute(
            "INSERT INTO votes (prompt_id, user_id, points) VALUES (%s, %s, %s);",
            (prompt_id, user_id, int(points))
        )
        db.execute('select check_prompt_activation(%s);', (prompt_id,))
    except:
        abort(500, message='Try later...')
    else:
        return jsonify({'message': 'Vote added successfully'}), 201

@bp.route('/')
@jwt_required()
@user_allowed(['admin', 'user'])
def get_votes():
    try:
        db = get_db()
        votes = db.execute("SELECT\
                            v.id,\
                            u.username,\
                            p.id AS prompt_id,\
                            p.prompt\
                            FROM votes v\
                            JOIN users u ON v.user_id = u.id\
                            JOIN prompts p ON v.prompt_id = p.id;").fetchall()
        return jsonify(votes), 200
    except:
        abort(500, message='Try later...')


"""@bp.route('/prompt/<int:prompt_id>/vote', methods=['POST'])
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

    return jsonify({'message': 'Vote added successfully'}), 201 """