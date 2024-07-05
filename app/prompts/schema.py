import marshmallow as ma

class PromptSchema(ma.Schema):
    id = ma.fields.Int(dump_only=True)
    prompt = ma.fields.Str(required=True)
    user_id = ma.fields.Int(required=True)
    statut_id = ma.fields.Int(required=True)
    created_at = ma.fields.DateTime(dump_only=True)
    updated_at = ma.fields.DateTime(dump_only=True)
