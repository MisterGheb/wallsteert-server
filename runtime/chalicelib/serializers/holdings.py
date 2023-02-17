import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()

class HoldingsSchema(Schema):
    id = fields.Integer()
    stocks = fields.String()
    total_volume = fields.Integer()
    avg_bid_price = fields.Decimal()


@leangle.add_schema()

class HoldingsResponseSchema(Schema):
    investment = fields.Decimal(dump_only=True)
    current_value = fields.Decimal(dump_only=True)
    stocks_possessed = fields.List(fields.Nested(HoldingsSchema))

    class Meta:
        unknown = EXCLUDE