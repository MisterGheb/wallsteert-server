import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class OhlcvSchema(Schema):
    open = fields.Number()
    high = fields.Number()
    low = fields.Number()
    close = fields.Number()
    volume = fields.Integer()
    id = fields.Number()

    market_id = fields.Integer(dump_only=False)
    stock_id = fields.Integer(dump_only=False)
    
    class Meta:
        unknown = EXCLUDE