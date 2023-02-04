import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError

from ..authorizer import token_auth
from ..models.users import Users
from ..serializers.users import UsersSchema
from ..constants import *

auth_routes = Blueprint('auth')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Auth"])
@leangle.describe.parameter(name='body', _in='body', description='Create a new User', schema='RegisterUserSchema')
@leangle.describe.response(200, description='Created', schema='UserSchema')
@auth_routes.route('/registration', methods=['POST'], cors=True)
def register_user():
    json_body = auth_routes.current_request.json_body
    if json_body.get('email') is None or json_body.get('password1') is None:
        raise BadRequestError(f"Password or email doesn't exists")
    if json_body.get('username') is None:
        json_body['username'] = json_body['email']
    json_body['password'] = bcrypt.hashpw(json_body['password1'].encode('utf-8'), bcrypt.gensalt())

    user_data = UserSchema().load(json_body)
    if User.where(email=user_data['email']).first() is not None:
        raise BadRequestError(f"User with email {user_data['email']} already exists")
    user = User.create(**user_data, token=binascii.hexlify(os.urandom(20)).decode())
    return UserSchema().dump(user)

@leangle.describe.tags(["Auth"])
@leangle.describe.parameter(name='body', _in='body', description='Login User', schema='LoginUserSchema')
@leangle.describe.response(200, description='User Details', schema='UserSchema')
@auth_routes.route('/login', methods=['POST'], cors=True, content_types=['application/json; charset=utf-8', 'application/json', 'application/x-www-form-urlencoded'])
def login_user():
    json_body = auth_routes.current_request.json_body
    if json_body.get('email') is None or json_body.get('password') is None:
        raise BadRequestError(f"Password or email doesn't exists")
    user = User.where(email=json_body['email']).first()
    if user is None:
        raise BadRequestError(f"User with email {json_body['email']} doesn't exists")
    
    if not bcrypt.checkpw(json_body['password'].encode('utf-8'), user.password.encode('utf-8')):
        raise UnauthorizedError(f"Username and password doesn't match")
    return UserSchema().dump(user)

@leangle.describe.tags(["Auth"])
@leangle.describe.response(200, description='User Details', schema='UserSchema')
@auth_routes.route('/user', methods=['GET'], cors=True, authorizer=token_auth)
def authorize_user():
    user_id = auth_routes.current_request.context['authorizer']['principalId']
    user = User.find_or_fail(user_id)
    return UserSchema().dump(user)

@leangle.describe.tags(["Auth"])
@leangle.describe.parameter(name='body', _in='body', description='Login User using dev-connect', schema='DevConnectSchema')
@leangle.describe.response(200, description='User Details', schema='UserSchema')
@auth_routes.route('/login/social/token/devconnect', methods=['POST'], cors=True)
def devconnect_login():
    url = DEVCONNECT_ISSUER_URL.rstrip("/") + "/protocol/openid-connect/token/"

    if auth_routes.current_request.json_body is None or auth_routes.current_request.json_body.get('code') is None:
        raise BadRequestError("Code Not Found")
    code = auth_routes.current_request.json_body.get('code')

    if auth_routes.current_request.json_body.get('redirect_uri') is None:
        raise BadRequestError("Redirect URI Not Found")
    redirect_uri = auth_routes.current_request.json_body.get('redirect_uri')

    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    post_data = {
        'client_id': DEVCONNECT_CLIENT_ID,
        'client_secret': DEVCONNECT_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(url, data=post_data, headers=header)

    if response.status_code != 200:
        logger.error(f"Unable to fetch Credentials using the provided Code")
        raise BadRequestError("Unable to fetch Credentials using the provided Code")
    
    body = response.json()
    logger.info(f"Auth Response Fetched")
    id_token = body['access_token']
    url = DEVCONNECT_ISSUER_URL.rstrip("/") + "/protocol/openid-connect/userinfo/"
    header = {
        'Authorization': 'Bearer ' + id_token
    }
    response = requests.get(url, headers=header)

    if response.status_code != 200:
        logger.error(f"Unable to fetch User Info from DevConnect")
        raise BadRequestError("Unable to fetch User Info from DevConnect")
    
    details = response.json()
    logger.info(f"User Info {details}")
    user = User.where(username=details['preferred_username']).first()
    if user is None:
        user = User.create(
            email = details['email'],
            username = details['preferred_username'],
            password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12)),
            first_name = details['given_name'],
            last_name = details['family_name'],
            ad_username = details['preferred_username'],
            token = binascii.hexlify(os.urandom(20)).decode()
        )
    return UserSchema().dump(user)


