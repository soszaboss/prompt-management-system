import marshmallow as ma

class GroupeSchema(ma.Schema):
    name = ma.fields.Str(required=True)
    description = ma.fields.Str()
    created_by = ma.fields.Int()
