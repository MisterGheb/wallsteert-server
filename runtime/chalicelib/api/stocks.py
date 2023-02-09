import logging
import requests
import random
import string
import os
import binascii
import leangle
import bcrypt
from chalice import Blueprint, BadRequestError, UnauthorizedError
from sqlalchemy import exc
from marshmallow import exceptions

from ..authorizer import token_auth
from ..models.stocks import Stocks
from ..serializers.stocks import StocksSchema
from ..constants import *

stocks_routes = Blueprint('stocks')
logger = logging.getLogger(__name__)

@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(name='body', _in='body', description='List all stocks available in the market', schema='StocksSchema')
@leangle.describe.response(200, description='Stocks Listed', schema='StocksSchema')
@stocks_routes.route('/', methods=['GET'], cors=True)
def list_stocks():
    stocks = Stocks.all()
    status = "Success"
    if(stocks==[]):
        status="No stocks in the system"
    return {'status': status, 'data': StocksSchema(many=True).dump(stocks)}


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(name='body', _in='body', description='Create a stock in the market', schema='StocksSchema')
@leangle.describe.response(200, description='Stock Created', schema='StocksSchema')
@stocks_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth)
def create_stock():
    json_body = stocks_routes.current_request.json_body

    try:
        data_obj = StocksSchema().load(json_body)
    except TypeError as ex:
        raise BadRequestError(ex)
    except exceptions.ValidationError as ex:
        raise BadRequestError(ex)

    try:
        stock = Stocks.create(**data_obj)
    except exc.IntegrityError as ex:
        raise BadRequestError(ex._message())

    return {'status': 'Success', 'data': StocksSchema().dump(stock)}


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(name='body', _in='body', description='Get Stock', schema='StocksSchema')
@leangle.describe.response(200, description='Stock Retrieved', schema='StocksSchema')
@stocks_routes.route('/{stock_id}', methods=['GET'], cors=True)
def get_stock(stock_id):
    stock = Stocks.where(id=stock_id).first()
    status = "Success"
    if(stock == None):
        status = "Stock not Found!"
    return {'status': status, 'data': StocksSchema().dump(stock)}