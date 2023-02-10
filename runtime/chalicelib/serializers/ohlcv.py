import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class OhlcvSchema(Schema):
    id = fields.Number(dump_only=True)
    open = fields.Number(dump_only=True)
    high = fields.Number(dump_only=True)
    low = fields.Number(dump_only=True)
    close = fields.Number(dump_only=True)
    volume = fields.Integer(dump_only=True)

    market_id = fields.Integer(dump_only=False)
    stock_id = fields.Integer(dump_only=False)

    class Meta:
        unknown = EXCLUDE