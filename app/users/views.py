from app.users import bp
from flask import jsonify
from flask_smorest import abort
from app.messages import Message
from app.db import get_db
from app.authentification.schema import UserSchema
from flask.views import MethodView
from app.users.schema import UserCrendentialsSchema

# End point to update and delete an user
@bp.route('/user/<int:id>')
class User(MethodView):
    @bp.response(status_code=204, schema=Message, description='Message shows user is deleted successfuly.')
    def delete(self, id):
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = %s;", (id,)).fetchone()
        if user is None:
            abort(404, message='User does not exist')
        else:
            db.execute("DELETE FROM users WHERE id=%s", (id,))
            return jsonify(message='User deleted successfully'), 204

    @bp.arguments(UserCrendentialsSchema, location='json', description='Update user.', as_kwargs=True)
    @bp.response(status_code=200, schema=Message, description='Sending update')
    def put(self, id, **kwargs):
        try:
            username = kwargs.get("username")
        except ValueError:
            username = None
        try:
            email = kwargs.get("email")
        except ValueError:
            email = None
        db = get_db()
        if email and username:
            if db.execute("SELECT * FROM users WHERE email = %s;", (email,)).fetchone():
                abort(409, message='Email already used.')
            elif db.execute("SELECT * FROM users WHERE username = %s;", (username,)).fetchone():
                abort(409, message='Username already used.')
            else:
                # Update user logic here
                db.execute("UPDATE users SET username=%s, email=%s WHERE id=%s;", (username, email, id,))
                return jsonify(message='User updated successfully'), 200
        elif email and username is None:
            # Create account logic here (email-only registration)
            db.execute("UPDATE users SET email=%s WHERE id=%s;", (email, id,))
            return jsonify(message='Account updated successfuly.'), 200
        elif email is None and username:
            # Create account logic here (username-only registration)
            db.execute("UPDATE users SET username=%s WHERE id=%s;", (username, id,))
            return jsonify(message='Account updated successfuly.'), 200
        else:
            abort(400, message='Empty fields.')


@bp.route('/')
@bp.response(200, UserSchema(many=True))
def get_users():
    db = get_db()
    users = db.execute("SELECT * FROM users;").fetchall()
    return users