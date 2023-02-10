import logging
import requests
import random
import string
import os
import re
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError, Response
from sqlalchemy import desc
import datetime


from ..authorizer import token_auth
from ..models.users import Users
from ..models.holdings import Holdings
from ..serializers.users import UsersSchema, SignupSchema
from ..serializers.holdings import HoldingsSchema
from ..constants import *

auth_routes = Blueprint('auth')
users_routes = Blueprint('users')
logger = logging.getLogger(__name__)


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='Create new user', schema='SignupSchema')
@leangle.describe.response(200, description='User Signed up', schema='SignupSchema')
@auth_routes.route('/signup', methods=['POST'], cors=True)
def register_user():
    json_body = auth_routes.current_request.json_body
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(not re.fullmatch(regex, json_body.get('email'))):
        raise BadRequestError("Email format is incorrect!")
    if json_body.get('email') is None or json_body.get('password') is None:
        raise BadRequestError("Password or email doesn't exists")
    if json_body.get('username') is None:
        json_body['username'] = json_body['email'].split('@')[0]
    json_body['password'] = bcrypt.hashpw(json_body['password'].encode('utf-8'), bcrypt.gensalt())

    user_data = SignupSchema().load(json_body)
    if Users.where(email=user_data['email']).first() is not None:
        raise BadRequestError(f"User with email {user_data['email']} already exists")
    user = Users.create(**user_data, token=binascii.hexlify(os.urandom(20)).decode(), available_funds=400000, blocked_funds=0)

    return {'id': user.id}


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Login', schema='LoginSchema')
@leangle.describe.response(200, description='User Logged in', schema='LoginSchema')
@auth_routes.route('/login', methods=['POST'], cors=True)
def login_user():
    json_body = auth_routes.current_request.json_body
    if json_body.get('email') is None or json_body.get('password') is None:
        raise BadRequestError(f"Password or email doesn't exists")
    user = Users.where(email=json_body['email']).first()
    if user is None:
        raise BadRequestError(f"User with email {json_body['email']} doesn't exists")

    if not bcrypt.checkpw(json_body['password'].encode('utf-8'), user.password.encode('utf-8')):
        raise UnauthorizedError(f"Username and password doesn't match")


    user.update(token=binascii.hexlify(os.urandom(20)).decode())
    user.update(loggedIn=True)
    return {'token':user.token}


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Logout', schema='LoginSchema')
@leangle.describe.response(204, description='User Loggedp out', schema='LoginSchema')
@auth_routes.route('/logout', methods=['POST'], cors=True,authorizer=token_auth)
def logout_user():
    user_id = auth_routes.current_request.context['authorizer']['principalId']
    user = Users.find_or_fail(user_id)
    user.update(token=None)
    user.update(loggedIn=False)
    return Response("" ,status_code=204)


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Profile', schema='UserSchema')
@leangle.describe.response(200, description='User Profile', schema='UserSchema')
@users_routes.route('/profile', methods=['GET'], cors=True)
def user_profile():
    user = Users.where(loggedIn=True).first()
    status= "Success"
    if(user==None):
        status = "No user currently logged in!"
        return {'status': status, 'data': {}}

    #return {UsersSchema().dump(user)}
    return {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "blocked_funds": user.blocked_funds,
            "available_funds": user.available_funds
            }

