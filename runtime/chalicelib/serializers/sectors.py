import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class SectorsSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE