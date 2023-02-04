import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class HoldingsSchema(Schema):
    id = fields.Integer(dump_only=False)
    volume = fields.Number()
    bid_price = fields.DateTime()
    bought_on = fields.Integer()
    user_id = fields.Integer(dump_only=False)
    stock_id = fields.Integer(dump_only=False)
    
    class Meta:
        unknown = EXCLUDE