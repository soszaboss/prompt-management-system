from app.users import bp
from flask_smorest import abort
from app.messages import Message
from app.db import get_db
from app.authentification.schemas import UserSchema
from flask.views import MethodView
from app.users.schema import UserCrendentialsSchema
from flask_jwt_extended import jwt_required, get_jwt
from app.decorators import user_allowed
import json
# End point to update and delete an user
@bp.route('/user/<int:id>')
class User(MethodView):
    @bp.response(status_code=204, description='Message shows user is deleted successfuly.')
    @jwt_required()
    @user_allowed('user')
    def delete(self, id):
        user_id = int(get_jwt()['sub'])
        if not user_id == id:
            abort(403, message='You can only delete an account of yourself if it is yours.')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = %s;", (id,)).fetchone()
        if user is None:
            abort(404, message='User does not exist')
        else:
            db.execute("DELETE FROM users WHERE id=%s", (id,))
            return '', 204

    @bp.arguments(UserCrendentialsSchema, location='json', description='Update user.', as_kwargs=True)
    @bp.response(status_code=200, description='Sending update')
    @jwt_required()
    @user_allowed('user')
    def put(self, id, **kwargs):
        user_id = int(get_jwt()['sub'])
        if not user_id == id:
            abort(403, message='You can only update an account of yourself if it is yours.')
       
        username = kwargs.get("username", None)
        email = kwargs.get("email", None)

        db = get_db()
        user = db.execute("select *from users where id = %s;", (id,)).fetchone()
        if user is not None:
            new_username = username if username is not None else user['username']
            new_email = email if email is not None else user['email']

            #check if email or username does not exist
            if db.execute("select *from users where (email = %s or username = %s) and id != %s;", (new_email, new_username, id,)).fetchone() is not None:
                abort(409, message='Email or username already used. Please choose another one.')
            db.execute("UPDATE users SET username=%s, email=%s WHERE id=%s;", (username, email, id,))
            return json.dumps({'message': 'User updated successfully'}), 200
        
        else:
            abort(400, message='User does not exist. Please enter valid user.')
    
    @bp.response(status_code=200, schema=UserSchema, description='Message shows user details.')
    @jwt_required()
    @user_allowed('admin')
    def get(self, id):
        db = get_db()
        try:
            user = db.execute("SELECT u.id, u.username, u.email,\
                    CASE \
                        WHEN u.role_id = 1 THEN 'admin' \
                        WHEN u.role_id = 2 THEN 'user' \
                        ELSE 'guest' \
                    END as role\
                    FROM users u where id = %s;", (id,)).fetchone()
        except:
            abort(500, message='Internal server error')
        else:
            if user is None:
                print(f"user {id} does not exist")
                abort(404, message='User does not exist')
            else:
                return user

@bp.route('/')
@bp.response(200, UserSchema(many=True))
@jwt_required()
@user_allowed('admin')
def get_users():
    db = get_db()
    users = db.execute("SELECT u.id, u.username, u.email,\
                   CASE \
                       WHEN u.role_id = 1 THEN 'admin' \
                       WHEN u.role_id = 2 THEN 'user' \
                       ELSE 'guest' \
                   END as role\
                   FROM users u;").fetchall()

    return users