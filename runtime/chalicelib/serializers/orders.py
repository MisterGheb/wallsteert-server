import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class OrdersSchema(Schema):
    id = fields.Integer(dump_only=True)
    bid_price = fields.Number(required=True)
    type = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    bid_volume = fields.Integer(required=True)
    executed_volume = fields.Integer(dump_only=True)
    user = fields.Integer(dump_only=True)
    stock = fields.Integer(required=True)
  
    
    class Meta:
        unknown = EXCLUDE