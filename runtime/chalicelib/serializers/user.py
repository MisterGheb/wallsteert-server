import leangle
from marshmallow import Schema, fields, EXCLUDE

@leangle.add_schema()
class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    username = fields.String(required=True)
    password = fields.String(load_only=True)
    first_name = fields.String()
    last_name = fields.String()
    token = fields.String(dump_only=True, data_key='key')
    ad_username = fields.String()
    
    class Meta:
        unknown = EXCLUDE



@leangle.add_schema()
class RegisterUserSchema(Schema):
    email = fields.Email(required=True)
    password1 = fields.String(required=True)
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    
    class Meta:
        unknown = EXCLUDE


@leangle.add_schema()
class LoginUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
    class Meta:
        unknown = EXCLUDE


@leangle.add_schema()
class DevConnectSchema(Schema):
    code = fields.String(load_only=True)
    redirect_uri = fields.String(load_only=True)
    
    class Meta:
        unknown = EXCLUDE