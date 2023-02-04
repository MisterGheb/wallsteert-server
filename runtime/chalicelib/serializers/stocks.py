import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class StocksSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    total_volume = fields.Integer()
    unallocated = fields.Integer()
    price = fields.Number()
    sector_id = fields.Integer()
    
    class Meta:
        unknown = EXCLUDE