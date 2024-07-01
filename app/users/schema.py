import marshmallow as ma

class UserCrendentialsSchema(ma.Schema):
    email = ma.fields.Str()
    username = ma.fields.Str()