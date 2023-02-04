import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class SectorsSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    
    class Meta:
        unknown = EXCLUDE