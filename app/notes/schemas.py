from marshmallow import Schema, fields

class NoteSchema(Schema):
    note = fields.Int(required=True)
    prompt_id = fields.Int(required=True)
