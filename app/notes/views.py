from app.notes import bp
from flask import jsonify
from flask_smorest import abort
from app.db import get_db
from app.notes.schemas import NoteSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed

# Endpoint pour gérer les notes
@bp.route('/note/<int:id>')
class NoteView(MethodView):
    @bp.response(200, description='Get note by id.')
    @jwt_required()
    def get(self, id):
        db = get_db()
        note = db.execute(
            "SELECT\
            n.id,\
            n.note,\
            u.username,\
            p.id AS prompt_id,\
            p.prompt\
            FROM notes n\
            JOIN users u ON n.user_id = u.id\
            JOIN prompts p ON n.prompt_id = p.id\
            WHERE n.id = %s;", (id,)
        ).fetchone()
        if note is None:
            abort(404, message='Note does not exist')
        return jsonify(note), 200

    @bp.response(204, description='Note successfully deleted.')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        try:
            db = get_db()
            note = db.execute("SELECT * FROM notes WHERE id = %s;", (id,)).fetchone()
            if note is None:
                abort(404, message='Note does not exist')
            db.execute("DELETE FROM notes WHERE id = %s;", (id,))
            return '', 204
        except:
            abort(500, message='Try later...')

    @bp.arguments(NoteSchema, location='json', description='Update note.', as_kwargs=True)
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, **kwargs):
        try:
            note = kwargs.get('note')
            prompt_id = kwargs.get('prompt_id', None)
            db = get_db()
            if note and prompt_id:
                db.execute(
                            "UPDATE notes SET note = %s, prompt_id = %s, updated_at = NOW() WHERE id = %s;",
                            (note, prompt_id, id)
                        )
            elif note and prompt_id is None:
                db.execute(
                            "UPDATE notes SET note = %s, updated_at = NOW() WHERE id = %s;",
                            (note, id)
                        )
            else:
                abort(400, message='Note does not exist.')
        except:
            abort(500, message='Try later...')
        else:
            return jsonify({'message': 'Note updated successfully'}), 200

@bp.route('/note/add', methods=['POST'])
@bp.arguments(NoteSchema, location='json', description='Add note.', as_kwargs=True)
@jwt_required()
def add_note(**kwargs):
    try:
        db = get_db()
        note = kwargs.get('note', None)
        if note is not None and -10 <= note <= 10:
            prompt_id = kwargs.get('prompt_id')
            user_id = int(get_jwt()['sub'])
            db.execute(
                "INSERT INTO notes (note, prompt_id, user_id) VALUES (%s, %s, %s);",
                (note, prompt_id, user_id)
            )
        else:
            abort(400, message='Note must be between -10 and 10.')
    except:
        abort(500, message='Try later...')
    return jsonify({'message': 'Note added successfully'}), 201

@bp.route('/notes')
@jwt_required()
def get_notes():
    try:
        db = get_db()
        notes = db.execute("SELECT\
                            n.id,\
                            n.note,\
                            u.username,\
                            p.id AS prompt_id,\
                            p.prompt\
                            FROM notes n\
                            JOIN users u ON n.user_id = u.id\
                            JOIN prompts p ON n.prompt_id = p.id;").fetchall()
        return jsonify(notes), 200
    except:
        abort(500, message='Try later...')


