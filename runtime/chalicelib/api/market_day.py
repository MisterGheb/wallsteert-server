import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import exc, update

from ..authorizer import token_auth
from ..models.market_day import Market_day
from ..serializers.market_day import Market_daySchema
from ..constants import *

market_day_routes = Blueprint('market_day')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Market Open', schema='Market_daySchema')
@leangle.describe.response(200, description='Market successfully opened', schema='Market_daySchema')
@market_day_routes.route('/open', methods=['POST'], cors=True)

def market_open():
    all_days = Market_day.all()
    if len(all_days) > 0 and all_days[-1].status == "OPEN":
        raise BadRequestError("Current day must be closed to open a new day")
    if len(all_days) == 0:
        new_day = Market_day.create(day=0, status='OPEN')
    else:
        last_day = all_days[-1]
        new_day = Market_day.create(day=(last_day.day+1), status='OPEN')
    # set_ohlcv(new_day.id)
    return {'status': 'Success', 'data': Market_daySchema().dump(new_day)}

# def set_ohlcv(market_day_id):
#     all_stocks = Stocks.all()
#     for stock in all_stocks:
#         OHLCV.create( market_id = market_day_id, stocks_id=stock.id, open=-1, high=-1, low=-1, close=-1, volume=0)

@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Market Close', schema='Market_daySchema')
@leangle.describe.response(200, description='Market successfully closed', schema='Market_daySchema')
@market_day_routes.route('/close', methods=['POST'], cors=True)

def market_close():
    all_days = Market_day.all()
    if all_days[-1].status == "CLOSE":
        raise BadRequestError("Current day must be opened to close a new day")
    else:
        last_day = all_days[-1]
        marketDay = Market_day.where(day=last_day.day).first().update(status="CLOSE")
    # close_ohlcv(new_day.id)
    return {'status': 'Success', 'data': Market_daySchema().dump(marketDay)}

@leangle.describe.tags(["Market_day"])
@leangle.describe.parameter(name='body', _in='body', description='Market Close', schema='Market_daySchema')
@leangle.describe.response(200, description='Market successfully closed', schema='Market_daySchema')
@market_day_routes.route('/', methods=['GET'], cors=True)



def list_market():
    market = Market_day.query.all()
    return {'status': 'Success', 'data': Market_daySchema().dump(market)}