import marshmallow as ma

class Message(ma.Schema):
    message = ma.fields.String()