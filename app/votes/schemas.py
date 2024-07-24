from marshmallow import Schema, fields

class VoteSchema(Schema):
    id = fields.Int(dump_only=True)
    points = fields.Int(dump_only=True, description="Vote value")
    prompt_id = fields.Int(required=True, description="ID of the related prompt")
    points = fields.Int(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    username = fields.String(dump_only=True)
