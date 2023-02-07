import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class StocksSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    total_volume = fields.Integer(required=True)
    unallocated = fields.Integer(required=True)
    price = fields.Number(required=True)
    sectors_id = fields.Integer(required=True)
    
    class Meta:
        unknown = EXCLUDE