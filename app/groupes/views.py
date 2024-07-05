from app.groupes import bp
from flask import jsonify
from flask_smorest import abort
from app.messages import Message
from app.db import get_db
from app.groupes.schema import GroupeSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.decorators import user_allowed

@bp.route('/groupe/<int:id>')
class Groupe(MethodView):
    @bp.response(status_code=204, schema=Message, description='Message shows groupe is deleted successfully.')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        db = get_db()
        groupe = db.execute("SELECT * FROM groupes WHERE id = %s;", (id,)).fetchone()
        if groupe is None:
            abort(404, message='Groupe does not exist')
        else:
            db.execute("DELETE FROM groupes WHERE id=%s", (id,))
            return jsonify(message='Groupe deleted successfully'), 204

    @bp.arguments(GroupeSchema, location='json', description='Update groupe.', as_kwargs=True)
    @bp.response(status_code=200, schema=Message, description='Sending update')
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, **kwargs):
        db = get_db()
        name = kwargs.get("name")
        description = kwargs.get("description")
        if name:
            if db.execute("SELECT * FROM groupes WHERE name = %s;", (name,)).fetchone():
                abort(409, message='Name already used.')
            else:
                db.execute("UPDATE groupes SET name=%s, description=%s WHERE id=%s;", (name, description, id,))
                return jsonify(message='Groupe updated successfully'), 200
        else:
            abort(400, message='Empty fields.')
    
    @bp.response(status_code=200, schema=GroupeSchema, description='Message shows groupe details.')
    @jwt_required()
    @user_allowed('admin')
    def get(self, id):
        db = get_db()
        groupe = db.execute("SELECT id, name, description, created_by FROM groupes WHERE id = %s;", (id,)).fetchone()
        if groupe is None:
            abort(404, message='Groupe does not exist')
        else:
            return groupe

@bp.route('/')
@bp.response(200, GroupeSchema(many=True))
@jwt_required()
@user_allowed('admin')
def get_groupes():
    db = get_db()
    groupes = db.execute("SELECT id, name, description, created_by FROM groupes;").fetchall()
    return groupes
