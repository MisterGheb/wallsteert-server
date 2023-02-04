import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class UsersSchema(Schema):
    id = fields.Integer(dump_only=False)
    name = fields.String()
    email = fields.String()
    available_funds = fields.Number()
    blocked_funds = fields.Number()
    
    class Meta:
        unknown = EXCLUDE



@leangle.add_schema()
class SignupSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password1 = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE


@leangle.add_schema()
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE