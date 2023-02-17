import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class UsersSchema(Schema):
    id = fields.Integer(dump_only=False)
    name = fields.String(required=True)
    email = fields.String(required=True)
    available_funds = fields.Number(dump_only=True)
    blocked_funds = fields.Number(dump_only=True)
    token = fields.String(dump_only=True)
    #loggedIn = fields.Bool(dump_only=True)
    
    class Meta:
        unknown = EXCLUDE


@leangle.add_schema()
class SignupSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE


@leangle.add_schema()
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE