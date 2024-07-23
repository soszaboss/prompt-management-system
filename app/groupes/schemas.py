import marshmallow as ma

class GroupeSchema(ma.Schema):
    id = ma.fields.Int(dump_only=True)
    name = ma.fields.Str()
    description = ma.fields.Str()
    created_by = ma.fields.Str(dump_only=True)
    created_at = ma.fields.DateTime(dump_only=True)
    updated_at = ma.fields.DateTime(dump_only=True)