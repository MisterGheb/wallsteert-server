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
    returnStocks = []
    for stock in stocks:
        print(f" helllllooooooooooooooooooooooooooooooooooo{stock.price}")
        returnStocks.append({
            "id": stock.id,
            "name": stock.name,
            "price": str(round(stock.price,2)),
            "sector": stock.sectors_id,
            "unallocated": stock.unallocated,
            "total_volume": stock.total_volume
        })
    return returnStocks


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(name='body', _in='body', description='Create a stock in the market', schema='StocksSchema')
@leangle.describe.response(200, description='Stock Created', schema='StocksSchema')
@stocks_routes.route('/', methods=['POST'], cors=True, authorizer=token_auth)
def create_stock():
    json_body = stocks_routes.current_request.json_body

    try:
        data_obj = StocksSchema().load(json_body)
    except TypeError as ex:
        return Response("", status_code=400)
    except exceptions.ValidationError as ex:
        return Response("", status_code=400)

    try:
        stock = Stocks.create(
            name = data_obj["name"],
            price = data_obj["price"],
            sectors_id = data_obj["sector"],
            unallocated = data_obj["unallocated"],
            total_volume = data_obj["total_volume"] 
        )
        
    except exc.IntegrityError as ex:
        return Response("", status_code=400)

    return { 
            "id": stock.id,          
            "name": stock.name,
            "price":str(round(stock.price,2)),
            "sector":stock.sectors_id,
            "unallocated": stock.unallocated,
            "total_volume": stock.total_volume 
            }


@leangle.describe.tags(["Stocks"])
@leangle.describe.parameter(name='body', _in='body', description='Get Stock', schema='StocksSchema')
@leangle.describe.response(200, description='Stock Retrieved', schema='StocksSchema')
@stocks_routes.route('/{stock_id}', methods=['GET'], cors=True)
def get_stock(stock_id):
    stock = Stocks.where(id=stock_id).first()
    status = "Success"
    if(stock == None):
        status = "Stock not Found!"

        
    return { 
            "id": stock.id,          
            "name": stock.name,
            "price":str(round(stock.price,2)),
            "sector":stock.sectors_id,
            "unallocated": stock.unallocated,
            "total_volume": stock.total_volume 
            }