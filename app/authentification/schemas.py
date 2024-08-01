import marshmallow as ma

class UserSchema(ma.Schema):
    id = ma.fields.Integer(dump_only=True)
    username = ma.fields.String(required=True, error_messages={"required": {"message": "Username required", "code": 400}})
    email = ma.fields.Email(required=True, error_messages={"required": {"message": "Email required", "code": 400}})
    password = ma.fields.String(required=True, load_only=True)
    confirm_password = ma.fields.String(required=True, load_only=True)
    role = ma.fields.String(dump_only=True)

class LoginShema(ma.Schema):
    email = ma.fields.Email(required=True, error_messages={"required": {"message": "Email required", "code": 400}})
    password = ma.fields.String(required=True, error_messages={"required": {"message": "Password required", "code": 400}})

class NewAccessTokenSchema(ma.Schema):
    new_access_token = ma.fields.UUID()
