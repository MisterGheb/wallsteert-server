import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class OrdersSchema(Schema):
    id = fields.Integer(dump_only=True)
    bid_price = fields.Number()
    type = fields.String()
    created_at = fields.Time()
    updated_at = fields.Time()
    status = fields.String()
    bid_volume = fields.Integer()
    executed_volume = fields.Integer()
    user_id = fields.Integer()
    stock_id = fields.Integer()
  
    
    class Meta:
        unknown = EXCLUDE