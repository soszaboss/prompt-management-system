from marshmallow import Schema, fields

class NoteSchema(Schema):
    note = fields.String(required=True, description="Note text")
    prompt_id = fields.Int(required=True, description="ID of the related prompt")
