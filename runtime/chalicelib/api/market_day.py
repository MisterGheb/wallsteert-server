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
from ..models.market_day import Market_day
from ..serializers.market_day import Market_daySchema
from ..constants import *

market_day_routes = Blueprint('market_day')
logger = logging.getLogger(__name__)


# MARKET DAY OPEN
@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Open the market for trading, start a new day', schema='Market_daySchema')
@leangle.describe.response(200, description='Market open for trading', schema='Market_daySchema')
@market_day_routes.route('/open', methods=['POST'], cors=True)

def sectors():
    
    market_dict = {"date":"20230201", "status":"open"}
    
    Market_day.create(**market_dict)


    return Market_daySchema().dump(market_day)


# MARKET DAY CLOSED

@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Close the market for all trading', schema='Market_daySchema')
@leangle.describe.response(200, description='Market closed for trading', schema='Market_daySchema')
@market_day_routes.route('/close', methods=['POST'], cors=True)

def sectors():
    json_body = market_day_routes.current_request.json_body
    data_body = Market_daySchema().load(json_body)

    try:
        market_day = Market_day.create(**data_body) 
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message())


    return Market_daySchema().dump(market_day)

@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Close the market for all trading', schema='Market_daySchema')
@leangle.describe.response(200, description='Market closed for trading', schema='Market_daySchema')
@market_day_routes.route('/ohlc', methods=['GET'], cors=True)

def sectors():
    json_body = market_day_routes.current_request.json_body
    data_body = Market_daySchema().load(json_body)

    try:
        market_day = Market_day.create(**data_body) 
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message())


    return Market_daySchema().dump(sectors)