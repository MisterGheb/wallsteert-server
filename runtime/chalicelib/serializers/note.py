import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class NoteSchema(Schema):
    id = fields.Integer(dump_only=True)
    content = fields.String()
    created_at = fields.DateTime(dump_only=True)
    created_by_id = fields.Integer(dump_only=True)
    
    class Meta:
        unknown = EXCLUDE
