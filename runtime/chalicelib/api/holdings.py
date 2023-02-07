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
from ..models.holdings import Holdings
from ..serializers.holdings import HoldingsSchema
from ..constants import *

holdings_routes = Blueprint('holdings')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Holdings"])
@leangle.describe.parameter(name='body', _in='body', description='List Holdings', schema='HoldingsSchema')
@leangle.describe.response(200, description='Holdings Listed', schema='HoldingsSchema')
@holdings_routes.route('/', methods=['GET'], cors=True)
def list_holdings():
    json_body = holdings_routes.current_request.json_body
    holdings = Holdings.all()

    return HoldingsSchema().dump(holdings)