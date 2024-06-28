import marshmallow as ma

class UserShema(ma.Schema):
    id = ma.fields.Integer()
    username = ma.fields.String(required=True)
    email = ma.fields.Email(required=True)
    password = ma.fields.String(required=True)
    confirm_password = ma.fields.String(required=True)
    role_id = ma.fields.Integer(required=True)