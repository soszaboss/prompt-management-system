from marshmallow import Schema, fields

class VoteSchema(Schema):
    vote = fields.Int(required=True, description="Vote value")
    prompt_id = fields.Int(required=True, description="ID of the related prompt")
