from app.groupes import bp
from flask import jsonify
from flask_smorest import abort
from app.messages import Message
from app.db import get_db
from app.groupes.schemas import GroupeSchema
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed, users_allowed

@bp.route('/groupe/<int:id>')
class Groupe(MethodView):
    @bp.response(status_code=204, description='Message shows groupe is deleted successfully.')
    @jwt_required()
    @user_allowed('admin')
    def delete(self, id):
        db = get_db()
        groupe = db.execute("SELECT * FROM groupes WHERE id = %s;", (id,)).fetchone()
        if groupe is None:
            abort(404, message='Groupe does not exist')
        else:
            db.execute("DELETE FROM groupes WHERE id=%s", (id,))
            return '', 204

    @bp.arguments(GroupeSchema, location='json', description='Update groupe.', as_kwargs=True)
    @bp.response(status_code=200, schema=Message, description='Sending update')
    @jwt_required()
    @user_allowed('admin')
    def put(self, id, **kwargs):
        db = get_db()
        name = kwargs.get("name", None)
        description = kwargs.get("description", None)
        
        # Vérifier si le groupe existe
        groupe = db.execute("SELECT * FROM groupes WHERE id = %s;", (id,)).fetchone()
        if groupe is None:
            abort(404, message='Groupe does not exist')

        # Vérifier si le nom est déjà utilisé par un autre groupe
        if name:
            if db.execute("SELECT * FROM groupes WHERE name = %s AND id != %s;", (name, id)).fetchone():
                abort(409, message='Name already used.')
        
        # Mettre à jour les informations du groupe
        new_name = name if name is not None else groupe['name']
        new_description = description if description is not None else groupe['description']
        
        # Mettre à jour le groupe dans la base de données
        db.execute("UPDATE groupes SET name=%s, description=%s WHERE id=%s;", (new_name, new_description, id))
        
        return '', 200

    @bp.response(status_code=200, schema=GroupeSchema, description='Message shows groupe details.')
    @jwt_required()
    @user_allowed('admin')
    def get(self, id):
        db = get_db()
        groupe = db.execute("SELECT g.id, g.name, g.description, u.username as created_by, g.created_at, g.updated_at\
                            FROM groupes g JOIN users u On g.created_by = u.id\
                            WHERE g.created_by = u.id and g.id = %s;", (id,)).fetchone()
        if groupe is None:
            abort(404, message='Groupe does not exist')
        else:
            return groupe

@bp.route('/', methods=['GET'])
@bp.response(200, GroupeSchema(many=True))
@jwt_required()
@user_allowed('admin')
def get_groupes():
    db = get_db()
    groupes = db.execute("SELECT g.id, g.name, g.description, u.username as created_by, g.created_at, g.updated_at\
                          FROM groupes g JOIN users u On g.created_by = u.id WHERE g.created_by = u.id;").fetchall()
    return groupes

@bp.route('/groupe/add', methods=['POST'])
@bp.arguments(GroupeSchema, location='json', description='Add groupe.', as_kwargs=True)
@jwt_required()
@user_allowed('admin')
def add_groupe(**kwargs):
    db = get_db()
    name = kwargs.get("name")
    description = kwargs.get("description", None)
    created_by = int(get_jwt()['sub'])
    try:
        db.execute("insert into groupes (name, description, created_by) values (%s, %s, %s);", (name, description, created_by,))
    except:
        abort(409, message='Name already used.')
    else:
        return jsonify({'message': 'Groupe added successfully'}), 201

@bp.route('/groupe/<int:groupe_id>/user/<int:user_id>', methods=['POST'])
@jwt_required()
@user_allowed('admin')
def add_groupe(groupe_id, user_id):
    pass