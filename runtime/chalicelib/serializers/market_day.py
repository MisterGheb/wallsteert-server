import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class Market_daySchema(Schema):
    id = fields.Integer(dump_only=False)
    day = fields.Integer()
    status = fields.String()
    
    class Meta:
        unknown = EXCLUDE