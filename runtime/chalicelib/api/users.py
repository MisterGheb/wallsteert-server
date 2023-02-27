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

from .market_day import initialize_ohlcv
from ..authorizer import token_auth
from ..models.market_day import Market_day
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
    """
    Allows a new user to signup
    
    """
    json_body = auth_routes.current_request.json_body
    # proper email format
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    print(f"this is the jsonbody{json_body}")
    print(type(json_body))
    if json_body.get('email') is None or json_body.get('password') is None:
        # if password or email is blank, throw error
        return Response("", status_code=400)
    if(not re.fullmatch(regex, json_body.get('email'))):
        # if email format does not match regex then throw error
        return Response("", status_code=400)
    if json_body.get('name') is None:
        # if there is no username then the username will be the part of the email before the @ in email
        json_body['name'] = json_body['email'].split('@')[0]
    json_body['password'] = bcrypt.hashpw(json_body['password'].encode(
        'utf-8'), bcrypt.gensalt())  # encrypt the password in the database

    user_data = SignupSchema().load(json_body)
    if Users.where(email=user_data['email']).first() is not None:
        return Response("", status_code=400)
    user = Users.create(**user_data, token=binascii.hexlify(os.urandom(20)
                                                            ).decode(), available_funds=400000.00, blocked_funds=0.00)

    all_days = Market_day.all()
    if len(all_days) == 0:
        new_day = Market_day.create(day=1, status='OPEN')
        initialize_ohlcv(Market_day.all()[-1].id)
    return {'id': user.id}


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Login', schema='LoginSchema')
@leangle.describe.response(200, description='User Logged in', schema='LoginSchema')
@auth_routes.route('/login', methods=['POST'], cors=True)
def login_user():
    """
    Allows a user to Login
    
    """
    json_body = auth_routes.current_request.json_body
    if json_body.get('email') is None or json_body.get('password') is None:
        return Response("", status_code=204)
    user = Users.where(email=json_body['email']).first()
    if user is None:
        return Response("", status_code=401)

    if not bcrypt.checkpw(json_body['password'].encode('utf-8'), user.password.encode('utf-8')):
        return Response("", status_code=401)

    user.update(token=binascii.hexlify(os.urandom(20)).decode())
    user.update(loggedIn=True)
    return {'token': user.token}


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Logout', schema='LoginSchema')
@leangle.describe.response(200, description='User Loggedp out', schema='LoginSchema')
@auth_routes.route('/logout', methods=['POST'], cors=True, authorizer=token_auth)
def logout_user():
    """
    Allows a user to logout
    
    """
    user_id = auth_routes.current_request.context['authorizer']['principalId']
    user = Users.find_or_fail(user_id)
    user.update(token=None)
    user.update(loggedIn=False)
    return Response("", status_code=204)


@leangle.describe.tags(["Users"])
@leangle.describe.parameter(name='body', _in='body', description='User Profile', schema='UserSchema')
@leangle.describe.response(200, description='User Profile', schema='UserSchema')
@users_routes.route('/profile', methods=['GET'], cors=True, authorizer=token_auth)
def user_profile():
    """
    Searches for a users profile
    
    """
    user_id = auth_routes.current_request.context['authorizer']['principalId']
    user = Users.where(id=user_id).first()
    if(user == None):
        return Response("", status_code=404)
    return_user = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "blocked_funds": ('%.2f' % user.blocked_funds),
        "available_funds": ('%.2f' % user.available_funds)
    }

    return return_user